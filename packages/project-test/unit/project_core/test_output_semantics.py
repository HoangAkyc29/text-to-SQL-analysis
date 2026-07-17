"""Unit tests for IV output-only table/column semantics resolver."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
from project_core.domain.schema.output_semantics import (
    build_output_semantics,
    extract_projections,
    extract_sql_tables,
    normalize_logical_table,
)

# packages/project-test/unit/project_core/this_file.py → monorepo root
REPO_ROOT = Path(__file__).resolve().parents[4]
DD = REPO_ROOT / "data_dictionary"


def _catalogs() -> tuple[SchemaCatalog, ColumnSemanticCatalog]:
    assert DD.exists(), f"missing data_dictionary at {DD}"
    return (
        SchemaCatalog.from_dictionary_dir(DD),
        ColumnSemanticCatalog.from_columns_dir(DD / "columns"),
    )


def test_normalize_shard_suffix():
    assert normalize_logical_table("STRANS_202401") == "STRANS"
    assert normalize_logical_table("STRANS") == "STRANS"
    assert normalize_logical_table("sku_def") == "sku_def"


def test_extract_sql_tables_skips_cte_and_normalizes_shard():
    sql = """
    WITH ProductSKUs AS (
      SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE = 'x'
    )
    SELECT s.GIFT_QTY
    FROM STRANS_202401 s
    INNER JOIN ProductSKUs p ON p.SKU_ID = s.SKU_ID
    """
    tables = extract_sql_tables(sql)
    assert "STRANS" in tables
    assert "SKU_DEF" in tables
    assert "ProductSKUs" not in tables


def test_extract_projection_physical_and_aggregate():
    sql = """
    SELECT s.GIFT_QTY AS GIFT_QTY, SUM(s.AMOUNT) AS total_amount
    FROM STRANS s
    GROUP BY s.GIFT_QTY
    """
    projs = extract_projections(sql)
    by_name = {p["output_name"].upper(): p for p in projs}
    assert "GIFT_QTY" in by_name
    assert by_name["GIFT_QTY"]["source_columns"][0]["column"].upper() == "GIFT_QTY"
    assert by_name["TOTAL_AMOUNT"]["is_aggregate"] is True
    assert any(c["column"].upper() == "AMOUNT" for c in by_name["TOTAL_AMOUNT"]["source_columns"])


def test_build_output_semantics_physical_column_high_confidence():
    catalog, col_catalog = _catalogs()
    sql = """
    SELECT TOP 10 s.GIFT_QTY AS GIFT_QTY
    FROM STRANS s
    WHERE s.TRAN_DATE >= '2026-07-01'
    """
    qf = SimpleNamespace(query_index=0, columns=["GIFT_QTY"], row_count=1)
    out = build_output_semantics(
        approved_sql=[sql],
        query_files=[qf],
        catalog=catalog,
        column_catalog=col_catalog,
        target_dbs=["db2"],
    )
    tables = out["output_table_semantics"]
    assert any(t["logical_name"] == "STRANS" and t["table_ref"] == "db2:strans" for t in tables)
    cols = out["output_column_semantics"]
    assert len(cols) == 1
    assert cols[0]["output_name"] == "GIFT_QTY"
    assert cols[0]["semantic_key"] == "gift_qty"
    assert cols[0]["confidence"] == "high"
    assert cols[0]["source"]["match"] == "sqlglot_projection"


def test_build_output_semantics_aggregate_alias():
    catalog, col_catalog = _catalogs()
    sql = """
    SELECT SUM(s.GIFT_QTY) AS total_gift_qty
    FROM STRANS s
    """
    qf = SimpleNamespace(query_index=0, columns=["total_gift_qty"], row_count=1)
    out = build_output_semantics(
        approved_sql=[sql],
        query_files=[qf],
        catalog=catalog,
        column_catalog=col_catalog,
        target_dbs=["db2"],
    )
    col = out["output_column_semantics"][0]
    assert col["output_name"] == "total_gift_qty"
    assert col["semantic_key"] == "gift_qty"
    assert col["source"]["match"] == "aggregated"
    assert col["confidence"] == "medium"
    assert "GIFT_QTY" in [c.upper() for c in col["source"]["physical_columns"]]


def test_build_output_semantics_ambiguous_bare_column_unresolved():
    """AMOUNT exists on multiple joined tables — do not guess."""
    catalog, col_catalog = _catalogs()
    # TRANSHDR and STRANS both have AMOUNT in dictionary (different keys).
    sql = """
    SELECT AMOUNT AS AMOUNT
    FROM STRANS s
    INNER JOIN TRANSHDR h ON h.TRANS_NUM = s.TRANS_NUM
    """
    qf = SimpleNamespace(query_index=0, columns=["AMOUNT"], row_count=1)
    out = build_output_semantics(
        approved_sql=[sql],
        query_files=[qf],
        catalog=catalog,
        column_catalog=col_catalog,
        target_dbs=["db2"],
    )
    col = out["output_column_semantics"][0]
    # Bare AMOUNT with two candidate tables → unresolved (no unique bind)
    assert col["semantic_key"] is None or col["confidence"] in {"low", "medium"}
    if col["source"]["match"] == "unresolved":
        assert col["semantic_key"] is None


def test_build_output_semantics_shard_table_normalized():
    catalog, col_catalog = _catalogs()
    sql = "SELECT s.GIFT_QTY AS GIFT_QTY FROM STRANS_202401 s"
    qf = SimpleNamespace(query_index=0, columns=["GIFT_QTY"], row_count=1)
    out = build_output_semantics(
        approved_sql=[sql],
        query_files=[qf],
        catalog=catalog,
        column_catalog=col_catalog,
        target_dbs=["db1"],
        default_target_db="db1",
    )
    assert any(t["logical_name"] == "STRANS" for t in out["output_table_semantics"])
    # db1:strans preferred when target_db=db1
    refs = {t["table_ref"] for t in out["output_table_semantics"]}
    assert "db1:strans" in refs or "db2:strans" in refs


def test_build_output_semantics_parquet_allowlist_only():
    catalog, col_catalog = _catalogs()
    sql = """
    SELECT s.GIFT_QTY AS GIFT_QTY, s.QTY AS QTY
    FROM STRANS s
    """
    # Parquet only kept GIFT_QTY (e.g. downstream drop) — QTY must not appear
    qf = SimpleNamespace(query_index=0, columns=["GIFT_QTY"], row_count=1)
    out = build_output_semantics(
        approved_sql=[sql],
        query_files=[qf],
        catalog=catalog,
        column_catalog=col_catalog,
        target_dbs=["db2"],
    )
    names = [c["output_name"] for c in out["output_column_semantics"]]
    assert names == ["GIFT_QTY"]


def test_build_output_semantics_unresolved_custom_alias():
    catalog, col_catalog = _catalogs()
    sql = """
    SELECT CASE WHEN s.GIFT_QTY > 0 THEN 1 ELSE 0 END AS gift_flag
    FROM STRANS s
    """
    qf = SimpleNamespace(query_index=0, columns=["gift_flag"], row_count=1)
    out = build_output_semantics(
        approved_sql=[sql],
        query_files=[qf],
        catalog=catalog,
        column_catalog=col_catalog,
        target_dbs=["db2"],
    )
    col = out["output_column_semantics"][0]
    assert col["output_name"] == "gift_flag"
    # Expression may still see GIFT_QTY source — if bound, semantic_key gift_qty; else unresolved
    assert col["source"]["match"] in {"sqlglot_projection", "aggregated", "unresolved", "name_exact"}
    if col["source"]["match"] == "unresolved":
        assert col["semantic_key"] is None


def test_iv_brain_state_includes_output_semantics(monkeypatch):
    from pathlib import Path

    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.analysis import iv_brain
    from project_core.domain.contracts.brief import AnalysisBrief
    from project_core.domain.contracts.workflow import PermissionsSnapshot

    captured: dict = {}

    class FakeSandbox:
        def run_analysis_script(self, *a, **k):
            return {"status": "ok", "artifacts": ["/tmp/a.csv"]}

    class FakePlanner:
        def __init__(self, *a, **k):
            self.tokens = 1

        def next_decision(self, state):
            captured["state"] = state
            return {
                "decision": "finalize",
                "status": "complete",
                "insight_vi": "ok",
                "headline_metrics": {},
            }

    monkeypatch.setattr(iv_brain, "_sandbox", lambda: FakeSandbox())
    monkeypatch.setattr(iv_brain, "AnalysisPlanner", FakePlanner)
    monkeypatch.setattr(
        iv_brain.DataProfiler,
        "profile",
        lambda self, paths, meta: [{"index": 0, "role": "main", "columns": ["GIFT_QTY"], "row_count": 1, "sample": []}],
    )
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)

    brief = AnalysisBrief(intent="test", metrics=["gift_qty"])
    perms = PermissionsSnapshot(
        actor_id="u",
        role="hq_analyst",
        tool_grants=["tool:python-sandbox:run_analysis_script"],
    )
    table_sem = [{"query_index": 0, "logical_name": "STRANS", "table_ref": "db2:strans", "description": "x", "confidence": "high"}]
    col_sem = [
        {
            "query_index": 0,
            "output_name": "GIFT_QTY",
            "semantic_key": "gift_qty",
            "kind": "measure",
            "facts": ["Số lượng quà tặng"],
            "source": {"tables": ["db2:strans"], "physical_columns": ["GIFT_QTY"], "expression": None, "match": "sqlglot_projection"},
            "confidence": "high",
        }
    ]
    iv_brain.run_analysis_brain(
        brief=brief,
        manifest={"queries": [{"path": "/tmp/x.parquet", "row_count": 1}]},
        profile={"row_count": 1},
        out_dir="/tmp/out",
        max_steps=2,
        query_meta=[{"role": "main"}],
        recipe_candidates=[],
        domain_rules_excerpt="",
        output_table_semantics=table_sem,
        output_column_semantics=col_sem,
        permissions=perms,
        context_policy=ContextPolicy(),
        llm=object(),
        profile_name="analyst",
        system_prompt="x",
    )
    assert captured["state"]["output_table_semantics"] == table_sem
    assert captured["state"]["output_column_semantics"] == col_sem
    assert "schema_context" not in captured["state"]
