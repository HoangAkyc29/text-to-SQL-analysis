from __future__ import annotations

from typing import Any

from project_core.config.loader import ProjectConfig, RoleConfig, load_project_config
from project_core.domain.contracts.workflow import PermissionsSnapshot


def role_config(role: str, config: ProjectConfig | None = None) -> RoleConfig:
    cfg = config or load_project_config()
    return cfg.roles.get(role, RoleConfig())


def build_permissions_snapshot(actor_id: str, role: str, store_ids: list[int] | None = None) -> PermissionsSnapshot:
    rc = role_config(role)
    return PermissionsSnapshot(
        actor_id=actor_id,
        role=role,
        allowed_tables=list(rc.allowed_tables),
        denied_columns=list(rc.denied_columns),
        store_ids=store_ids,
        store_filter_required=rc.store_filter_required,
        tool_grants=_default_tool_grants(role),
    )


def _default_tool_grants(role: str) -> list[str]:
    grants = [
        "tool:sql-gateway:validate",
        "tool:sql-gateway:explain",
        "tool:sql-gateway:execute",
        "tool:python-sandbox:execute",
    ]
    return grants


def can_access_table(snapshot: PermissionsSnapshot, table: str) -> bool:
    return table.lower() in {t.lower() for t in snapshot.allowed_tables}
