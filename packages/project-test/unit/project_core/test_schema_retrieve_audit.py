"""Schema retrieve audit helpers."""

from __future__ import annotations

from project_core.domain.audit.logger import AuditLogger
from project_core.domain.audit.schema_retrieve import build_schema_retrieve_payload


def test_build_schema_retrieve_payload_compacts_hits():
    payload = build_schema_retrieve_payload(
        actor_id="actor-1",
        sql_attempt=2,
        retrieval_payload={
            "phase": "hierarchical",
            "facets": ["Lọc theo mã hàng", "Bill tối thiểu 600k"],
            "query": "intent blob",
            "top_k": 20,
            "columns": [
                {
                    "semantic_key": "gift_qty",
                    "score": 0.91,
                    "text": "GIFT_QTY " + ("x" * 300),
                    "tables": [{"ref": "db2:strans", "role": "fact"}],
                }
            ],
            "tables": [
                {
                    "table_ref": "db2:strans",
                    "score": 0.88,
                    "text": "STRANS line sales",
                }
            ],
            "candidate_tables": ["db2:strans", "db2:transhdr"],
            "candidate_semantic_keys": ["gift_qty", "bill_amount"],
        },
        miss=False,
    )
    assert payload["facets"] == ["Lọc theo mã hàng", "Bill tối thiểu 600k"]
    assert payload["n_columns"] == 1
    assert payload["n_tables"] == 1
    assert payload["columns"][0]["semantic_key"] == "gift_qty"
    assert payload["columns"][0]["tables"] == ["db2:strans"]
    assert len(payload["columns"][0]["text_preview"]) <= 160
    assert "…" in payload["columns"][0]["text_preview"]
    assert payload["candidate_tables"] == ["db2:strans", "db2:transhdr"]
    assert payload["miss"] is False
    assert "text" not in payload["columns"][0]


def test_audit_logger_persists_schema_retrieve(tmp_path, monkeypatch):
    path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SQL_AUDIT_LOG_PATH", str(path))
    audit = AuditLogger()
    event_id = audit.log_schema_retrieve(
        trace_id="trace-1",
        actor_id="actor-1",
        payload=build_schema_retrieve_payload(
            actor_id="actor-1",
            sql_attempt=1,
            retrieval_payload={
                "phase": "hierarchical",
                "facets": ["facet-a"],
                "columns": [],
                "tables": [],
                "candidate_tables": [],
                "candidate_semantic_keys": [],
            },
            miss=True,
        ),
    )
    events = audit.events()
    assert len(events) == 1
    assert events[0]["event_type"] == "schema_retrieve"
    assert events[0]["payload"]["event_id"] == event_id
    assert events[0]["payload"]["facets"] == ["facet-a"]
    assert events[0]["payload"]["miss"] is True
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert '"schema_retrieve"' in lines[0]
