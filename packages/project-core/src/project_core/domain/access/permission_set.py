"""Capability-based permission model (DB-driven, wildcard-aware).

A capability is a string key in one of three namespaces:

- ``data:table:<NAME>``      access to a logical table (``data:table:*`` = all)
- ``data:column_deny:<COL>`` deny a column (applies on top of table access)
- ``data:store_filter:required`` force per-store filtering
- ``tool:<server>:<action>`` invoke an MCP tool (``tool:*`` = all)
- ``function:<tool_id>``     run a promoted sandbox recipe (``function:*`` = all)

Wildcards use a ``:*`` suffix at any segment boundary, e.g. ``tool:*`` or
``tool:sql-gateway:*``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from project_core.domain.contracts.workflow import PermissionsSnapshot

CAP_DATA_TABLE = "data:table:"
CAP_DATA_COLUMN_DENY = "data:column_deny:"
CAP_DATA_STORE_FILTER = "data:store_filter:required"
CAP_TOOL_PREFIX = "tool:"
CAP_FUNCTION_PREFIX = "function:"

# Canonical capability key for each MCP tool name exposed by the agents.
MCP_TOOL_CAPABILITY: dict[str, str] = {
    "validate_sql": "tool:sql-gateway:validate",
    "explain_sql": "tool:sql-gateway:explain",
    "get_schema_snapshot": "tool:sql-gateway:explain",
    "execute_readonly": "tool:sql-gateway:execute",
    "run_analysis_script": "tool:python-sandbox:run_analysis_script",
    "preview_dataframe": "tool:python-sandbox:preview_dataframe",
    "load_dataset": "tool:python-sandbox:load_dataset",
    "merge_datasets": "tool:python-sandbox:merge_datasets",
    "plot_chart": "tool:python-sandbox:plot_chart",
    "export_excel": "tool:python-sandbox:export_excel",
    "run_recipe_tool": "tool:python-sandbox:run_recipe_tool",
}

# Full tool capability set (used for the admin/full-access role).
ALL_TOOL_CAPABILITIES: tuple[str, ...] = tuple(sorted(set(MCP_TOOL_CAPABILITY.values())))

# Single source of truth for which MCP tool names each pipeline agent may call.
# ContextPolicy.allowed_mcp_tools derives from this; do not hardcode elsewhere.
AGENT_TOOLS: dict[str, tuple[str, ...]] = {
    "II": ("validate_sql",),
    "III": ("explain_sql", "get_schema_snapshot"),
    "IV": (
        "run_analysis_script",
        "preview_dataframe",
        "export_excel",
        "plot_chart",
        "load_dataset",
        "merge_datasets",
    ),
}


def capability_granted(grants: Iterable[str] | None, key: str) -> bool:
    """Return True if ``key`` is covered by ``grants`` (exact or wildcard)."""
    if not grants:
        return False
    grant_set = grants if isinstance(grants, (set, frozenset)) else set(grants)
    if key in grant_set:
        return True
    parts = key.split(":")
    for i in range(1, len(parts)):
        if ":".join(parts[:i]) + ":*" in grant_set:
            return True
    return False


def tool_capability_for(tool_name: str) -> str:
    """Map an MCP tool name to its canonical capability key."""
    return MCP_TOOL_CAPABILITY.get(tool_name, f"{CAP_TOOL_PREFIX}{tool_name}")


def grant_denial(
    grants: Iterable[str] | None, capability: str, violation: str
) -> dict[str, Any] | None:
    """Shared default-deny gate: return a ``policy_blocked`` payload when
    ``capability`` is not covered by ``grants``, else ``None``.

    Used by MCP servers (sql-gateway, python-sandbox) so the deny shape and
    wildcard semantics stay identical across enforcement points.
    """
    if capability_granted(grants, capability):
        return None
    return {
        "error": "policy_blocked",
        "status": "policy_blocked",
        "violations": [violation],
    }


@dataclass(frozen=True)
class PermissionSet:
    """Resolved set of capability keys for a single actor."""

    keys: frozenset[str]

    @classmethod
    def from_keys(cls, keys: Iterable[str]) -> "PermissionSet":
        return cls(frozenset(k.strip() for k in keys if k and k.strip()))

    @classmethod
    def full_access(cls) -> "PermissionSet":
        return cls(frozenset({"data:table:*", "tool:*", "function:*"}))

    def _wants_all_tables(self) -> bool:
        return "data:table:*" in self.keys or "data:*" in self.keys

    def to_snapshot(
        self,
        *,
        actor_id: str,
        role: str,
        store_ids: list[int] | None,
        all_tables: Iterable[str],
    ) -> "PermissionsSnapshot":
        from project_core.domain.contracts.workflow import PermissionsSnapshot

        if self._wants_all_tables():
            allowed_tables = sorted({t for t in all_tables})
        else:
            allowed_tables = sorted(
                k[len(CAP_DATA_TABLE):]
                for k in self.keys
                if k.startswith(CAP_DATA_TABLE) and not k.endswith(":*")
            )
        denied_columns = sorted(
            k[len(CAP_DATA_COLUMN_DENY):]
            for k in self.keys
            if k.startswith(CAP_DATA_COLUMN_DENY) and not k.endswith(":*")
        )
        tool_grants = sorted(k for k in self.keys if k.startswith(CAP_TOOL_PREFIX))
        allowed_functions = sorted(k for k in self.keys if k.startswith(CAP_FUNCTION_PREFIX))
        return PermissionsSnapshot(
            actor_id=actor_id,
            role=role,
            allowed_tables=allowed_tables,
            denied_columns=denied_columns,
            store_ids=store_ids,
            store_filter_required=CAP_DATA_STORE_FILTER in self.keys,
            tool_grants=tool_grants,
            allowed_functions=allowed_functions,
        )
