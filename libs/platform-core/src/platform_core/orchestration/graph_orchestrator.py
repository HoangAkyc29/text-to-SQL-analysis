"""Item 25 concrete - graph orchestration from config.

Delegates to :class:`GraphEngine` in agent-core for DAG / parallel / conditional
execution. The graph is data, not code: reorder or add nodes by editing YAML.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from commons.logging import get_logger

from agent_core.io.schemas import AgentRequest, AgentResponse
from agent_core.multiagent.event_bus.base import EventBus
from agent_core.multiagent.orchestration.graph import GraphEngine
from agent_core.multiagent.runtime.base import SyncRuntime
from agent_core.multiagent.runtime.thread_pool import ThreadPoolRuntime

from agent_core.multiagent.communication.factory import build_event_bus
from platform_core.config.schema import PlatformConfig
from platform_core.router.message_router import MessageRouter

log = get_logger("platform_core.orchestrator")


def _build_runtime(config: PlatformConfig) -> SyncRuntime | ThreadPoolRuntime:
    orch = config.orchestration
    if orch.runtime == "thread_pool":
        return ThreadPoolRuntime(max_workers=orch.max_workers)
    return SyncRuntime()


class GraphOrchestrator:
    """Execute the agent graph defined in the platform config."""

    def __init__(
        self,
        config: PlatformConfig,
        router: MessageRouter,
        *,
        event_bus: EventBus | None = None,
        runtime: SyncRuntime | ThreadPoolRuntime | None = None,
    ) -> None:
        self.config = config
        self.router = router
        self.event_bus = event_bus or build_event_bus(config.communication.event_bus)
        self.runtime = runtime or _build_runtime(config)

    def run(self, goal: str, *, inputs: dict[str, Any] | None = None, actor_id: str = "platform") -> dict[str, Any]:
        plan = self.config.orchestration.to_execution_plan()
        session_id = f"sess-{uuid4().hex[:8]}"

        def executor(node_id: str, request_dict: dict[str, Any]) -> AgentResponse:
            request = AgentRequest(**request_dict)
            return self.router.send_to_agent(node_id, request)

        engine = GraphEngine(
            plan,
            executor,
            runtime=self.runtime,
            event_bus=self.event_bus,
        )
        result = engine.run(goal, inputs=inputs, session_id=session_id, actor_id=actor_id)

        log.info("Graph order: %s", " -> ".join(result.order))
        workflow = result.workflow
        return {
            "goal": result.goal,
            "inputs": result.inputs,
            "order": result.order,
            "execution_levels": result.execution_levels,
            "node_outputs": result.node_outputs,
            "skipped_nodes": result.skipped_nodes,
            "parallel_groups": result.parallel_groups,
            "final": result.final,
            "final_content": result.final_content,
            "shared_state": result.shared_state,
            "workflow": {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status.value,
                "current_node": workflow.current_node,
                "completed_nodes": list(workflow.completed_nodes),
            }
            if workflow is not None
            else None,
        }
