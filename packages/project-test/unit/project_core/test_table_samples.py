"""Unit tests for static table sample catalog."""

from __future__ import annotations

import json
from pathlib import Path
import random

from project_core.domain.schema.table_samples import (
    infer_sample_data_sources,
    is_null_or_zero,
    load_table_samples,
    looks_like_code_or_id_column,
    normalize_sample_table_key,
    pick_quality_rows,
    row_null_or_zero_score,
    sanitize_sample_value,
)
from project_core.text.tcvn3 import tcvn3_to_unicode


def test_null_or_zero_score_prefers_dense_rows():
    sparse = {"a": None, "b": 0, "c": "", "d": 5}
    dense = {"a": 1, "b": 2, "c": "x", "d": 5}
    assert row_null_or_zero_score(sparse) > row_null_or_zero_score(dense)
    assert is_null_or_zero(0)
    assert is_null_or_zero("   ")  # whitespace-only == null
    assert is_null_or_zero("\t")
    assert not is_null_or_zero(False)


def test_sanitize_strips_and_keeps_id_code_as_string():
    assert sanitize_sample_value("STK_ID", "10005       ") == "10005"
    assert sanitize_sample_value("SKU_CODE", "00030344") == "00030344"
    assert sanitize_sample_value("SKU_CODE", 30344) == "30344"  # already lost zeros upstream
    assert isinstance(sanitize_sample_value("AMOUNT", 0), int)
    assert sanitize_sample_value("FULL_NAME", "  abc  ") == "abc"
    assert looks_like_code_or_id_column("SKU_CODE")
    assert looks_like_code_or_id_column("STK_ID")
    assert not looks_like_code_or_id_column("SKU")  # boolean flag on SKU_DEF


def test_sanitize_applies_tcvn3():
    assert sanitize_sample_value("REMARK", "§") == "Đ"
    assert sanitize_sample_value("REMARK", "ng©n") == "ngân"
    raw = "C©n ®èi"
    assert sanitize_sample_value("REMARK", raw) == tcvn3_to_unicode(raw)
    assert sanitize_sample_value("REMARK", raw) != raw


def test_pick_quality_rows_prefers_dense_then_diversity():
    rows = [
        {"v": None},  # empty
        {"v": 0},  # empty
        {"a": 1, "b": 10, "c": 100},
        {"a": 1, "b": 10, "c": 100},  # duplicate of above
        {"a": 2, "b": 20, "c": 200},
        {"a": 3, "b": 30, "c": 300},
        {"a": 1, "b": 99, "c": 999},  # overlaps on a with first dense
    ]
    picked = pick_quality_rows(rows, n=3, rng=random.Random(0))
    assert len(picked) == 3
    # No exact duplicate rows
    fps = {json.dumps(r, sort_keys=True) for r in picked}
    assert len(fps) == 3
    # Should start from a dense row (quality), not the null/zero-only ones
    assert all(not (set(r.keys()) == {"v"} and is_null_or_zero(r.get("v"))) for r in picked)


def test_pick_quality_rows_breaks_mono_categorical():
    """A new TRANS_CODE must beat another clone of the mono code even if other cols differ."""
    rows = [
        {"TRANS_CODE": "113", "SKU_ID": "A", "AMOUNT": 1},
        {"TRANS_CODE": "113", "SKU_ID": "B", "AMOUNT": 2},
        {"TRANS_CODE": "113", "SKU_ID": "C", "AMOUNT": 3},
        {"TRANS_CODE": "113", "SKU_ID": "D", "AMOUNT": 4},
        {"TRANS_CODE": "221", "SKU_ID": "E", "AMOUNT": 5},
        {"TRANS_CODE": "114", "SKU_ID": "F", "AMOUNT": 6},
    ]
    picked = pick_quality_rows(rows, n=3, rng=random.Random(0))
    codes = {r["TRANS_CODE"] for r in picked}
    assert "221" in codes or "114" in codes
    assert len(codes) >= 2


def test_pick_quality_rows_strips_output():
    rows = [{"STK_ID": "10005       ", "NOTE": "  x  ", "AMOUNT": 1}] * 5
    picked = pick_quality_rows(rows, n=1, rng=random.Random(1))
    assert picked[0]["STK_ID"] == "10005"
    assert picked[0]["NOTE"] == "x"


def test_normalize_shard_names():
    assert normalize_sample_table_key("STRANS_202607") == "STRANS"
    assert normalize_sample_table_key("dbo.PMTRANS_202401") == "PMTRANS"
    assert normalize_sample_table_key("TRANSHDR_ARC") == "TRANSHDR_ARC"
    assert normalize_sample_table_key("SKU_DEF") == "SKU_DEF"


def test_infer_sample_data_sources_strans_history():
    assert infer_sample_data_sources("STRANS", hint="db1") == ["db1"]
    assert infer_sample_data_sources("STRANS", needs_db1=True, needs_db2=False) == ["db1"]
    assert infer_sample_data_sources("STRANS", needs_db1=False, needs_db2=True) == ["db2"]
    assert infer_sample_data_sources("STRANS", needs_db1=True, needs_db2=True) == ["db2", "db1"]
    assert infer_sample_data_sources("STRANS_202503") == ["db1"]
    assert infer_sample_data_sources("TRANSHDR_ARC") == ["db1"]


def test_load_strans_db1_and_dual():
    one = load_table_samples(["STRANS"], target_dbs=["db1"], allowed_tables=["STRANS"])
    assert len(one) == 1
    assert one[0].get("error") is None
    assert one[0]["data_source"] == "db1"
    assert one[0]["row_count"] == 5

    dual = load_table_samples(
        ["STRANS"],
        allowed_tables=["STRANS"],
        needs_db1=True,
        needs_db2=True,
    )
    assert len(dual) == 2
    assert {d["data_source"] for d in dual} == {"db1", "db2"}
    assert all(d.get("error") is None for d in dual)


def test_load_table_samples_missing_and_acl(tmp_path: Path):
    root = tmp_path / "table_samples" / "db2"
    root.mkdir(parents=True)
    (root / "ONLY.json").write_text(
        json.dumps(
            {
                "table": "ONLY",
                "data_source": "db2",
                "columns": ["A"],
                "rows": [{"A": 1}] * 5,
            }
        ),
        encoding="utf-8",
    )
    samples = load_table_samples(
        ["ONLY", "MISSING", "BLOCKED"],
        allowed_tables=["ONLY", "MISSING"],
        root=tmp_path / "table_samples",
    )
    assert samples[0]["table"] == "ONLY"
    assert samples[1]["error"] == "sample_missing"
    assert samples[2]["error"] == "table_not_allowed"


def test_explicit_db_hint_does_not_fallback_to_other_db(tmp_path: Path):
    """db1 request must not silently return db2 samples when db1 file is absent."""
    db2 = tmp_path / "table_samples" / "db2"
    db2.mkdir(parents=True)
    (db2 / "CRDTRANS.json").write_text(
        json.dumps(
            {
                "table": "CRDTRANS",
                "data_source": "db2",
                "columns": ["A"],
                "rows": [{"A": 1}] * 5,
            }
        ),
        encoding="utf-8",
    )
    samples = load_table_samples(
        ["CRDTRANS"],
        allowed_tables=["CRDTRANS"],
        needs_db1=True,
        needs_db2=False,
        root=tmp_path / "table_samples",
    )
    assert len(samples) == 1
    assert samples[0]["error"] == "sample_missing"
