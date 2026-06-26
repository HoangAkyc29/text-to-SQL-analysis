"""Graph execution engine: DAG, parallel, conditional routing, debate, shared state."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from agent_core.multiagent.event_bus.base import Event, EventBus, InMemoryEventBus
from agent_core.multiagent.orchestration.graph.builder import routes_from_spec
from agent_core.multiagent.orchestration.graph.conditions import ConditionEvaluator
from agent_core.multiagent.orchestration.graph.merge import merge_results, merge_state_map
from agent_core.multiagent.orchestration.graph.model import ExecutionPlan, GraphNodeSpec, GraphRunResult
from agent_core.multiagent.orchestration.graph.runtime_helpers import (
    debate_turn_metadata,
    parse_executor_result,
    speakers_for_round,
)
from agent_core.multiagent.runtime.base import Runtime, SyncRuntime
from agent_core.state.shared_state.in_memory import InMemoryBlackboard
from agent_core.state.workflow_state.base import WorkflowState, WorkflowStatus

NodeExecutor = Callable[[str, dict[str, Any]], Any]


class GraphEngine:
    """Execute a validated :class:`ExecutionPlan`."""

    def __init__(
        self,
        plan: ExecutionPlan,
        executor: NodeExecutor,
        *,
        runtime: Runtime | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.plan = plan
        self.executor = executor
        self.runtime = runtime or SyncRuntime()
        self.event_bus = event_bus or InMemoryEventBus()

    def run(
        self,
        goal: str,
        *,
        inputs: dict[str, Any] | None = None,
        session_id: str,
        actor_id: str = "platform",
    ) -> GraphRunResult:
        run_context = dict(inputs or {})
        inbox: dict[str, Any] = {}
        outputs: dict[str, Any] = {}
        order: list[str] = []
        execution_levels: list[list[str]] = []
        skipped: list[str] = []
        parallel_groups: list[list[str]] = []
        completed: set[str] = set()

        blackboard = InMemoryBlackboard(schema=self.plan.state_schema)
        workflow = WorkflowState(workflow_id=session_id, status=WorkflowStatus.RUNNING)

        preds: dict[str, set[str]] = defaultdict(set)
        for e in self.plan.edges:
            preds[e.target].add(e.source)

        def shared_state() -> dict[str, Any]:
            return blackboard.snapshot()

        def eval_ctx() -> dict[str, Any]:
            last = order[-1] if order else ""
            return {
                "inbox": inbox,
                "payload": outputs.get(last, {}),
                "inputs": run_context,
                "goal": goal,
                "shared_state": shared_state(),
            }

        def make_request(
            level_inbox: dict[str, Any],
            *,
            debate: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            metadata: dict[str, Any] = {
                **run_context,
                "inbox": dict(level_inbox),
                "shared_state": shared_state(),
            }
            if debate is not None:
                metadata["debate"] = debate
            return {
                "message": goal,
                "session_id": session_id,
                "actor_id": actor_id,
                "metadata": metadata,
            }

        def apply_state_updates(updates: dict[str, Any]) -> None:
            if updates:
                blackboard.apply_updates(updates)

        def run_agent(agent_id: str, request: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
            result = self.executor(agent_id, request)
            payload, state_updates = parse_executor_result(result)
            apply_state_updates(state_updates)
            return payload, state_updates

        def execute_debate(node_id: str, spec: GraphNodeSpec, level_inbox: dict[str, Any]) -> Any:
            transcript: list[Any] = list(blackboard.read(spec.transcript_channel, []) or [])
            turn_outputs: list[Any] = []

            for round_idx in range(spec.max_rounds):
                for speaker in speakers_for_round(spec, round_idx):
                    request = make_request(
                        level_inbox,
                        debate=debate_turn_metadata(
                            node_id=node_id,
                            round_idx=round_idx,
                            speaker=speaker,
                            participants=spec.participants,
                            transcript=transcript,
                        ),
                    )
                    payload, state_updates = run_agent(speaker, request)
                    turn = {
                        "round": round_idx,
                        "speaker": speaker,
                        "content": payload,
                        "state_updates": state_updates,
                    }
                    transcript.append(turn)
                    turn_outputs.append(turn)
                    apply_state_updates({spec.transcript_channel: [turn]})
                    self.event_bus.publish(
                        Event(
                            topic=f"{node_id}.debate.round_{round_idx}",
                            source=speaker,
                            payload=turn,
                        )
                    )

            facilitator_payload: Any = None
            if spec.facilitator:
                request = make_request(
                    level_inbox,
                    debate=debate_turn_metadata(
                        node_id=node_id,
                        round_idx=spec.max_rounds,
                        speaker=spec.facilitator,
                        participants=spec.participants,
                        transcript=transcript,
                        role="facilitator",
                    ),
                )
                facilitator_payload, facilitator_updates = run_agent(spec.facilitator, request)
                apply_state_updates(facilitator_updates)
            else:
                facilitator_payload = turn_outputs[-1]["content"] if turn_outputs else {}

            output_channel = spec.output_channel or node_id
            if facilitator_payload is not None:
                apply_state_updates({output_channel: facilitator_payload})

            return {
                "transcript": transcript,
                "decision": facilitator_payload,
                "output_channel": output_channel,
            }

        def execute_node(node_id: str, level_inbox: dict[str, Any]) -> Any:
            spec = self.plan.nodes.get(node_id)
            request = make_request(level_inbox)
            workflow.current_node = node_id

            if spec is None or spec.kind == "agent":
                payload, _ = run_agent(node_id, request)
                return payload

            if spec.kind == "parallel":
                parallel_groups.append(list(spec.agents))

                def _run_one(agent: str) -> tuple[str, Any, dict[str, Any]]:
                    agent_request = make_request(level_inbox)
                    payload, state_updates = run_agent(agent, agent_request)
                    return agent, payload, state_updates

                agent_outputs = self.runtime.map(_run_one, list(spec.agents))

                if spec.merge == "state_map":
                    node_output = merge_state_map(spec.state_map, agent_outputs)
                    blackboard.apply_updates(node_output)
                    return node_output

                payloads = [item[1] for item in agent_outputs]
                return merge_results(spec.merge, payloads)

            if spec.kind == "conditional":
                target = ConditionEvaluator(eval_ctx()).pick_route(routes_from_spec(spec))
                if target is None:
                    skipped.append(node_id)
                    return {}
                return {"_routed_to": target}

            if spec.kind == "join":
                parts = [inbox[src] for src in sorted(preds.get(node_id, set())) if src in inbox]
                return merge_results("concat", parts)

            if spec.kind == "debate":
                return execute_debate(node_id, spec, level_inbox)

            payload, _ = run_agent(node_id, request)
            return payload

        ready: set[str] = {self.plan.entry}

        while ready:
            level = sorted(ready)
            ready = set()
            execution_levels.append(level)
            level_inbox = dict(inbox)

            for node_id in level:
                if node_id in completed:
                    continue
                payload = execute_node(node_id, level_inbox)
                outputs[node_id] = payload
                inbox[node_id] = payload
                completed.add(node_id)
                order.append(node_id)
                workflow.mark_done(node_id, payload)
                self.event_bus.publish(
                    Event(topic=f"{node_id}.completed", source=node_id, payload=payload or {})
                )

            cond = ConditionEvaluator(eval_ctx())
            for e in self.plan.edges:
                if e.source not in completed or e.target in completed:
                    continue

                src_payload = outputs.get(e.source)
                if isinstance(src_payload, dict) and "_routed_to" in src_payload:
                    if e.target == src_payload["_routed_to"]:
                        ready.add(e.target)
                    continue

                if e.when is not None and not cond.matches(e.when):
                    skipped.append(f"{e.source}->{e.target}")
                    continue

                if preds[e.target].issubset(completed):
                    ready.add(e.target)

        workflow.status = WorkflowStatus.COMPLETED
        workflow.current_node = order[-1] if order else None
        last_id = order[-1] if order else ""
        last_payload = outputs.get(last_id)

        return GraphRunResult(
            goal=goal,
            inputs=run_context,
            order=order,
            execution_levels=execution_levels,
            node_outputs=outputs,
            skipped_nodes=skipped,
            parallel_groups=parallel_groups,
            final=last_payload,
            final_content=str(last_payload) if last_payload is not None else "",
            shared_state=shared_state(),
            workflow=workflow,
        )
