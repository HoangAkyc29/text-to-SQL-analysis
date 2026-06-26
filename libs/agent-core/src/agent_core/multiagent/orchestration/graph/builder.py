"""Build and validate execution plans from graph specs."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from agent_core.multiagent.orchestration.graph.model import (
    ConditionalRoute,
    ExecutionPlan,
    GraphEdgeSpec,
    GraphNodeSpec,
)


class GraphBuildError(ValueError):
    """Raised when the graph definition is invalid."""


def build_plan(
    *,
    entry: str,
    edges: list[GraphEdgeSpec],
    nodes: dict[str, GraphNodeSpec] | None = None,
    state_schema: Any | None = None,
) -> ExecutionPlan:
    """Validate *edges* + *nodes* and return an :class:`ExecutionPlan`."""
    nodes = nodes or {}
    if not entry:
        raise GraphBuildError("graph entry is required")

    all_ids: set[str] = {entry}
    for e in edges:
        all_ids.add(e.source)
        all_ids.add(e.target)
    all_ids.update(nodes.keys())

    for nid, spec in nodes.items():
        if spec.kind == "parallel" and not spec.agents:
            raise GraphBuildError(f"parallel node '{nid}' requires agents")
        if spec.kind == "conditional" and not spec.routes:
            raise GraphBuildError(f"conditional node '{nid}' requires routes")
        if spec.kind == "debate" and not spec.participants:
            raise GraphBuildError(f"debate node '{nid}' requires participants")
        if spec.kind == "parallel" and spec.merge == "state_map" and not spec.state_map:
            raise GraphBuildError(f"parallel node '{nid}' with merge=state_map requires state_map")

    _detect_cycle(entry, edges, all_ids)

    return ExecutionPlan(
        entry=entry,
        edges=edges,
        nodes=nodes,
        all_node_ids=all_ids,
        state_schema=state_schema,
    )


def _detect_cycle(entry: str, edges: list[GraphEdgeSpec], all_ids: set[str]) -> None:
    adj: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = {n: 0 for n in all_ids}
    for e in edges:
        adj[e.source].append(e.target)
        indegree[e.target] = indegree.get(e.target, 0) + 1
        indegree.setdefault(e.source, indegree.get(e.source, 0))

    queue: deque[str] = deque([n for n, d in indegree.items() if d == 0])
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for nxt in adj.get(node, []):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    if visited < len(indegree):
        raise GraphBuildError("graph contains a cycle")

    if entry not in all_ids:
        raise GraphBuildError(f"entry node '{entry}' not found in graph")


def linear_order(plan: ExecutionPlan) -> list[str]:
    """Backward-compatible linear order for simple chains (no branching)."""
    nxt = {e.source: e.target for e in plan.edges if e.when is None}
    order = [plan.entry]
    cur = plan.entry
    seen = {cur}
    while cur in nxt and nxt[cur] not in seen:
        cur = nxt[cur]
        order.append(cur)
        seen.add(cur)
    return order


def routes_from_spec(spec: GraphNodeSpec) -> list[tuple[str | None, str]]:
    return [(r.when, r.target) for r in spec.routes]


def conditional_routes_from_dicts(
    routes: list[dict[str, str]],
) -> list[ConditionalRoute]:
    out: list[ConditionalRoute] = []
    for r in routes:
        if "else" in r:
            out.append(ConditionalRoute(target=r["else"], when=None))
        else:
            out.append(ConditionalRoute(target=r["to"], when=r.get("when")))
    return out
