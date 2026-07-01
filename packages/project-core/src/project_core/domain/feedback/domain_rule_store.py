from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from project_core.domain.contracts.feedback import DomainRuleCandidate


class DomainRuleStore:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def stage_candidate(self, candidate: DomainRuleCandidate | dict[str, Any], *, trace_id: str) -> str:
        if isinstance(candidate, DomainRuleCandidate):
            data = candidate.model_dump()
        else:
            data = dict(candidate)
        rule_id = data.get("rule_id") or str(uuid4())
        record = {
            "rule_id": rule_id,
            "scope": data.get("scope", "general"),
            "statement": data.get("statement", ""),
            "evidence_trace_ids": list(data.get("evidence_trace_ids") or [trace_id]),
            "status": "candidate",
            "created_at": datetime.utcnow(),
        }
        self.collection.update_one({"rule_id": rule_id}, {"$set": record}, upsert=True)
        return rule_id

    def confirm(self, rule_id: str, *, confirmed_by: str = "user") -> None:
        self.collection.update_one(
            {"rule_id": rule_id},
            {"$set": {"status": "confirmed", "confirmed_by": confirmed_by, "confirmed_at": datetime.utcnow()}},
        )

    def reject(self, rule_id: str) -> None:
        self.collection.update_one(
            {"rule_id": rule_id},
            {"$set": {"status": "rejected", "rejected_at": datetime.utcnow()}},
        )

    def confirmed_rules(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self.collection.find({"status": "confirmed"}).limit(limit))

    def excerpt_for_agents(self, max_chars: int = 4000) -> str:
        lines = ["# Confirmed domain rules"]
        for rule in self.confirmed_rules():
            lines.append(f"- [{rule.get('scope')}]: {rule.get('statement')}")
        text = "\n".join(lines)
        return text[:max_chars]
