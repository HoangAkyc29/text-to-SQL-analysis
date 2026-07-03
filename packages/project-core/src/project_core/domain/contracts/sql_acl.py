from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from project_core.domain.contracts.workflow import PermissionsSnapshot


class SqlAclContext(BaseModel):
    actor_id: str
    allowed_tables: list[str] = Field(default_factory=list)
    denied_columns: list[str] = Field(default_factory=list)
    store_ids: list[int] | None = None
    store_filter_required: bool = False
    tool_grants: list[str] = Field(default_factory=list)
    role: str = ""

    @classmethod
    def from_permissions(cls, permissions: PermissionsSnapshot) -> SqlAclContext:
        return cls(
            actor_id=permissions.actor_id,
            allowed_tables=list(permissions.allowed_tables),
            denied_columns=list(permissions.denied_columns),
            store_ids=permissions.store_ids,
            store_filter_required=permissions.store_filter_required,
            tool_grants=list(permissions.tool_grants),
            role=permissions.role,
        )

    def to_gateway_args(self) -> dict[str, object]:
        return {
            "actor_id": self.actor_id,
            "allowed_tables": self.allowed_tables,
            "denied_columns": self.denied_columns,
            "store_ids": self.store_ids,
            "store_filter_required": self.store_filter_required,
            "tool_grants": self.tool_grants,
        }
