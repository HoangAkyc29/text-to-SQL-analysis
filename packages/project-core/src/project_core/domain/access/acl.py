from __future__ import annotations

from project_core.config.loader import ProjectConfig, RoleConfig, load_project_config
from project_core.domain.access.permission_set import PermissionSet
from project_core.domain.contracts.workflow import PermissionsSnapshot


def role_config(role: str, config: ProjectConfig | None = None) -> RoleConfig:
    cfg = config or load_project_config()
    return cfg.roles.get(role, RoleConfig())


def _default_all_tables() -> list[str]:
    from project_core.domain.schema.catalog import SchemaCatalog

    return SchemaCatalog.from_dictionary_dir().logical_table_names()


def build_permissions_snapshot(
    actor_id: str,
    role: str,
    store_ids: list[int] | None = None,
    *,
    permission_set: PermissionSet | None = None,
    all_tables: list[str] | None = None,
) -> PermissionsSnapshot:
    """Build a PermissionsSnapshot.

    - Production/DB path: pass an explicit ``permission_set`` (resolved from the
      AUTH DB) plus the catalog ``all_tables`` used to expand ``data:table:*``.
    - Dev/test fallback (``ALLOW_DEV_AUTH=1``): reads role capabilities from
      ``config/project.yaml`` verbatim. Grants are **fail-closed**: a role that
      omits ``tool_grants``/``allowed_functions`` gets none (deny), matching the
      DB path. Roles must declare their grants explicitly.
    """
    if permission_set is not None:
        tables = all_tables if all_tables is not None else _default_all_tables()
        return permission_set.to_snapshot(
            actor_id=actor_id,
            role=role,
            store_ids=store_ids,
            all_tables=tables,
        )

    rc = role_config(role)
    return PermissionsSnapshot(
        actor_id=actor_id,
        role=role,
        allowed_tables=list(rc.allowed_tables),
        denied_columns=list(rc.denied_columns),
        store_ids=store_ids,
        store_filter_required=rc.store_filter_required,
        tool_grants=list(rc.tool_grants),
        allowed_functions=list(rc.allowed_functions),
    )
