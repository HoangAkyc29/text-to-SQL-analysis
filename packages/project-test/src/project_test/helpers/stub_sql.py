from __future__ import annotations

from typing import Any


class StubSqlGateway:
    def __init__(self, *, rows: list[dict[str, Any]] | None = None, policy_block: bool = False) -> None:
        self.rows = rows if rows is not None else [{"customer_id": 1, "total_amount": 100}]
        self.policy_block = policy_block
        self.executed: list[str] = []

    def validate_sql(self, sql: str, actor_id: str) -> dict[str, Any]:
        if self.policy_block:
            return {"allowed": False, "violations": ["blocked"]}
        return {"allowed": True, "sanitized_sql": sql}

    def explain_sql(self, sql: str, actor_id: str) -> dict[str, Any]:
        return {"status": "ok", "plan_rows": 1}

    def execute_readonly(self, sql: str, actor_id: str) -> dict[str, Any]:
        if self.policy_block:
            return {"error": "policy_blocked", "violations": ["blocked"]}
        self.executed.append(sql)
        return {"rows": self.rows, "columns": list(self.rows[0].keys()) if self.rows else []}
