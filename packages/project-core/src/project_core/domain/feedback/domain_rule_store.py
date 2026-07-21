from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from project_core.domain.contracts.feedback import DomainEvidence, DomainRuleCandidate


_EXPLICIT_SOURCES = frozenset({"user_statement", "clarification"})
_DATA_SOURCES = frozenset({"data_observation", "dictionary", "case_study", "external_document"})


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: Any) -> datetime | None:
    if not isinstance(value, datetime):
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


class DomainRuleStore:
    """Lifecycle store for reusable, declarative domain facts.

    The store deliberately contains no domain facts or SQL.  It only evaluates
    provenance, authority, scope and freshness.
    """

    def __init__(self, collection: Any, *, data_confirm_confidence: float | None = None) -> None:
        self.collection = collection
        configured = (
            float(os.getenv("DOMAIN_FACT_AUTO_CONFIRM_CONFIDENCE", "0.9"))
            if data_confirm_confidence is None
            else data_confirm_confidence
        )
        self.data_confirm_confidence = min(1.0, max(0.0, configured))

    def stage_candidate(self, candidate: DomainRuleCandidate | dict[str, Any], *, trace_id: str) -> str:
        model = candidate if isinstance(candidate, DomainRuleCandidate) else DomainRuleCandidate.model_validate(candidate)
        data = model.model_dump()
        rule_id = data.get("rule_id") or str(uuid4())
        new_evidence = self._normalize_evidence(model.evidence, trace_id=trace_id)
        existing = self.collection.find_one({"rule_id": rule_id})
        evidence = self._merge_evidence((existing or {}).get("evidence") or [], new_evidence)
        trace_ids = list(
            dict.fromkeys(
                [
                    *((existing or {}).get("evidence_trace_ids") or []),
                    *(data.get("evidence_trace_ids") or []),
                    trace_id,
                ]
            )
        )
        schema_links = self._normalize_schema_links(
            [
                *((existing or {}).get("schema_links") or []),
                *model.schema_links,
                *(link for item in evidence for link in item["schema_links"]),
            ]
        )
        created_at = (existing or {}).get("created_at") or _utc_now()
        record = {
            "rule_id": rule_id,
            "fact_type": model.fact_type,
            "scope": model.scope,
            "actor_id": model.actor_id,
            "tenant_id": model.tenant_id,
            "statement": model.statement.strip(),
            "evidence_trace_ids": trace_ids,
            "evidence": evidence,
            "schema_links": schema_links,
            "confidence": model.confidence,
            "authority": model.authority,
            "valid_from": model.valid_from,
            "valid_to": model.valid_to,
            "supersedes_rule_id": model.supersedes_rule_id,
            "status": "candidate",
            "stale": False,
            "created_at": created_at,
            "updated_at": _utc_now(),
        }
        record["conflict"] = self._has_conflict(record, exclude_rule_id=rule_id)
        auto_reason = self._auto_confirmation_reason(record)
        if auto_reason and not record["conflict"]:
            record.update(
                status="confirmed",
                confirmed_by=auto_reason,
                confirmed_at=_utc_now(),
                decision_reason=auto_reason,
            )
        if existing and existing.get("status") in {"confirmed", "rejected"}:
            for key in (
                "status",
                "stale",
                "confirmed_by",
                "confirmed_at",
                "rejected_by",
                "rejected_at",
                "reviewer_role",
                "decision_reason",
                "stale_by",
                "stale_at",
                "superseded_by",
            ):
                if key in existing:
                    record[key] = existing[key]
        self.collection.update_one({"rule_id": rule_id}, {"$set": record}, upsert=True)
        return rule_id

    def review(
        self,
        rule_id: str,
        *,
        action: str,
        actor_id: str,
        role: str = "requester",
        tenant_id: str = "",
    ) -> dict[str, Any]:
        record = self.collection.find_one({"rule_id": rule_id})
        if not record:
            raise KeyError(rule_id)
        if action not in {"confirm", "reject", "stale"}:
            raise ValueError("unsupported domain-rule review action")
        if not self._can_review(
            record, action=action, actor_id=actor_id, role=role, tenant_id=tenant_id
        ):
            raise PermissionError("not authorized to review this domain rule")
        now = _utc_now()
        if action == "confirm":
            update = {
                "status": "confirmed",
                "stale": False,
                "confirmed_by": actor_id,
                "confirmed_at": now,
                "reviewer_role": role,
            }
            superseded_id = record.get("supersedes_rule_id")
            if superseded_id:
                self.collection.update_one(
                    {"rule_id": superseded_id},
                    {"$set": {"stale": True, "stale_at": now, "superseded_by": rule_id}},
                )
        elif action == "reject":
            update = {"status": "rejected", "rejected_by": actor_id, "rejected_at": now}
        else:
            update = {"stale": True, "stale_by": actor_id, "stale_at": now}
        self.collection.update_one(
            {"rule_id": rule_id},
            {"$set": {**update, "updated_at": now}},
        )
        return {**record, **update, "updated_at": now}

    def confirm(
        self,
        rule_id: str,
        *,
        confirmed_by: str = "user",
        role: str = "requester",
        tenant_id: str = "",
    ) -> None:
        self.review(
            rule_id,
            action="confirm",
            actor_id=confirmed_by,
            role=role,
            tenant_id=tenant_id,
        )

    def reject(
        self,
        rule_id: str,
        *,
        rejected_by: str = "user",
        role: str = "requester",
        tenant_id: str = "",
    ) -> None:
        self.review(
            rule_id,
            action="reject",
            actor_id=rejected_by,
            role=role,
            tenant_id=tenant_id,
        )

    def list_rules(
        self,
        *,
        actor_id: str,
        tenant_id: str = "",
        role: str = "requester",
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = {} if status is None else {"status": status}
        records = list(self.collection.find(query))
        visible = [
            item
            for item in records
            if self._scope_visible(item, actor_id=actor_id, tenant_id=tenant_id, role=role)
        ]
        visible.sort(
            key=lambda item: (
                _as_utc(item.get("updated_at"))
                or _as_utc(item.get("created_at"))
                or datetime.min.replace(tzinfo=timezone.utc)
            ),
            reverse=True,
        )
        return visible[: max(0, limit)]

    def confirmed_rules(
        self,
        limit: int = 50,
        *,
        actor_id: str = "",
        tenant_id: str = "",
        role: str = "requester",
        schema_links: list[dict[str, str]] | None = None,
        at: datetime | None = None,
    ) -> list[dict[str, Any]]:
        now = _as_utc(at) or _utc_now()
        requested_links = self._schema_link_keys(schema_links or [])
        records = self.list_rules(
            actor_id=actor_id,
            tenant_id=tenant_id,
            role=role,
            status="confirmed",
            limit=max(limit * 4, limit),
        )
        eligible: list[dict[str, Any]] = []
        for item in records:
            item_links = self._schema_link_keys(item.get("schema_links") or [])
            if not item_links or (requested_links and item_links.isdisjoint(requested_links)):
                continue
            valid_from = _as_utc(item.get("valid_from"))
            valid_to = _as_utc(item.get("valid_to"))
            if item.get("stale") or (valid_from and valid_from > now) or (valid_to and valid_to <= now):
                continue
            eligible.append(item)
            if len(eligible) >= limit:
                break
        return eligible

    def excerpt_for_agents(
        self,
        max_chars: int = 4000,
        *,
        actor_id: str = "",
        tenant_id: str = "",
        role: str = "requester",
        schema_links: list[dict[str, str]] | None = None,
    ) -> str:
        lines = ["# Confirmed domain rules"]
        for rule in self.confirmed_rules(
            actor_id=actor_id,
            tenant_id=tenant_id,
            role=role,
            schema_links=schema_links,
        ):
            lines.append(f"- [{rule.get('scope')}]: {rule.get('statement')}")
        text = "\n".join(lines)
        return text[:max_chars]

    def _auto_confirmation_reason(self, record: dict[str, Any]) -> str | None:
        evidence = record["evidence"]
        source_kinds = {item["source_kind"] for item in evidence}
        authority = record["authority"]
        explicit = bool(source_kinds & _EXPLICIT_SOURCES)
        authorized_high_authority = authority in {"domain_owner", "admin"} and explicit
        if record["scope"] == "global" and authority != "admin":
            return None
        if record.get("supersedes_rule_id") and not authorized_high_authority:
            return None
        if authorized_high_authority:
            return f"explicit_{authority}"
        if (
            authority == "requester"
            and record["scope"] == "user"
            and record["actor_id"]
            and explicit
        ):
            return "explicit_requester_user_scope"
        groups = {
            item["independent_group"]
            for item in evidence
            if item["source_kind"] in _DATA_SOURCES
            and item["confidence"] >= self.data_confirm_confidence
            and item["independent_group"]
        }
        if (
            source_kinds
            and source_kinds <= _DATA_SOURCES
            and record["confidence"] >= self.data_confirm_confidence
            and len(groups) >= 2
            and record["scope"] != "global"
        ):
            return "independent_data_evidence"
        return None

    def _has_conflict(self, record: dict[str, Any], *, exclude_rule_id: str) -> bool:
        for existing in self.collection.find({"status": "confirmed"}):
            if existing.get("rule_id") == exclude_rule_id or existing.get("stale"):
                continue
            same_scope = (
                existing.get("scope") == record["scope"]
                and existing.get("actor_id", "") == record["actor_id"]
                and existing.get("tenant_id", "") == record["tenant_id"]
            )
            links_overlap = bool(
                self._schema_link_keys(existing.get("schema_links") or [])
                & self._schema_link_keys(record["schema_links"])
            )
            if (
                same_scope
                and links_overlap
                and existing.get("fact_type") == record["fact_type"]
                and existing.get("statement", "").strip().casefold()
                != record["statement"].casefold()
            ):
                return True
        return False

    @staticmethod
    def _normalize_evidence(
        evidence: list[DomainEvidence], *, trace_id: str
    ) -> list[dict[str, Any]]:
        normalized = []
        for item in evidence:
            data = item.model_dump()
            data["evidence_id"] = item.evidence_id or str(uuid4())
            data["trace_id"] = item.trace_id or trace_id
            # quote is intentionally copied verbatim for auditability.
            normalized.append(data)
        return normalized

    @staticmethod
    def _merge_evidence(
        existing: list[dict[str, Any]], incoming: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        for item in [*existing, *incoming]:
            identity = (
                item.get("evidence_id")
                or (
                    item.get("source_kind"),
                    item.get("source_ref"),
                    item.get("quote"),
                    item.get("trace_id"),
                ),
            )
            if identity in seen:
                continue
            seen.add(identity)
            merged.append(dict(item))
        return merged

    @staticmethod
    def _normalize_schema_links(links: list[dict[str, str]]) -> list[dict[str, str]]:
        unique: dict[tuple[tuple[str, str], ...], dict[str, str]] = {}
        for link in links:
            clean = {str(key): str(value) for key, value in link.items() if value}
            if clean:
                unique[tuple(sorted(clean.items()))] = clean
        return list(unique.values())

    @staticmethod
    def _schema_link_keys(links: list[dict[str, str]]) -> set[tuple[tuple[str, str], ...]]:
        return {
            tuple(sorted((str(key), str(value)) for key, value in link.items() if value))
            for link in links
            if link
        }

    @staticmethod
    def _scope_visible(
        record: dict[str, Any], *, actor_id: str, tenant_id: str, role: str
    ) -> bool:
        scope = record.get("scope")
        if role == "admin":
            return True
        if scope == "global":
            return True
        if scope == "tenant":
            return bool(tenant_id) and record.get("tenant_id") == tenant_id
        return bool(actor_id) and record.get("actor_id") == actor_id

    @staticmethod
    def _can_review(
        record: dict[str, Any],
        *,
        action: str,
        actor_id: str,
        role: str,
        tenant_id: str,
    ) -> bool:
        if role == "admin":
            return True
        if role == "domain_owner":
            return record.get("scope") != "global" and (
                record.get("scope") == "user"
                or (bool(tenant_id) and record.get("tenant_id") == tenant_id)
            )
        return (
            action in {"confirm", "reject"}
            and record.get("scope") == "user"
            and record.get("actor_id") == actor_id
            and record.get("authority") == "requester"
            and not record.get("conflict")
            and not record.get("supersedes_rule_id")
        )
