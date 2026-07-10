"""Agent II plan audit payload helpers."""

from __future__ import annotations

from project_core.domain.audit.agent_ii_plan import build_agent_ii_plan_payload, plan_sql_workflow_summary
from project_core.domain.audit.logger import AuditLogger
from project_core.domain.contracts.agent_outputs import SqlPlannerResponse


def test_build_agent_ii_plan_payload_includes_full_sql():
    parsed = SqlPlannerResponse.model_validate(
        {
            "action": "plan_sql",
            "sql_queries": [
                "SELECT TOP 5 SKU_ID FROM SKU_DEF WHERE SKU_CODE = '0030344'",
                "SELECT TOP 5 s.SKU_ID FROM STRANS s WHERE s.TRANS_CODE = '113'",
            ],
            "query_meta": [{"role": "probe", "purpose": "sku_lookup"}, {"role": "main", "purpose": "gift_sales"}],
            "target_dbs": ["db2", "db2"],
            "target_db": "db2",
            "reasoning": "Probe SKU rồi fact STRANS",
            "schema_tables_used": ["SKU_DEF", "STRANS"],
            "semantic_keys_used": ["sale_line_sku_id"],
        }
    )
    payload = build_agent_ii_plan_payload(parsed, sql_attempt=2, usage_tokens=1200)
    assert payload["sql_attempt"] == 2
    assert payload["action"] == "plan_sql"
    assert payload["reasoning"] == "Probe SKU rồi fact STRANS"
    assert len(payload["queries"]) == 2
    assert payload["queries"][0]["sql"].startswith("SELECT TOP 5 SKU_ID")
    assert payload["queries"][0]["query_meta"]["role"] == "probe"
    assert payload["queries"][0]["target_db"] == "db2"
    assert len(payload["queries"][0]["sql_hash"]) == 16


def test_plan_sql_workflow_summary_truncates_reasoning():
    payload = {
        "action": "probe_sql",
        "sql_attempt": 1,
        "queries": [{}],
        "reasoning": "x" * 300,
    }
    summary = plan_sql_workflow_summary(payload, max_reasoning=50)
    assert summary.startswith("action=probe_sql;sql_attempt=1;n_queries=1;reasoning=")
    assert len(summary) < 120


def test_audit_logger_log_agent_ii_plan():
    audit = AuditLogger()
    event_id = audit.log_agent_ii_plan(
        trace_id="trace-1",
        actor_id="actor-1",
        payload={"action": "plan_sql", "queries": []},
    )
    events = audit.events()
    assert len(events) == 1
    assert events[0]["event_type"] == "agent_ii_plan"
    assert events[0]["trace_id"] == "trace-1"
    assert events[0]["payload"]["event_id"] == event_id
    assert events[0]["payload"]["actor_id"] == "actor-1"
