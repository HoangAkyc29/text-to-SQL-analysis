"""Unit tests for static table sample catalog."""

from __future__ import annotations

import json
from pathlib import Path

from project_core.domain.schema.table_samples import (
    is_null_or_zero,
    load_table_samples,
    looks_like_code_or_id_column,
    normalize_sample_table_key,
    pick_quality_rows,
    row_null_or_zero_score,
    sanitize_sample_value,
)


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


def test_pick_quality_rows_fills_from_next_tiers():
    rows = [
        {"v": None},  # score 1
        {"v": 0},  # score 1
        {"v": 9},  # score 0 — best
    ]
    picked = pick_quality_rows(rows, n=2, rng=__import__("random").Random(0))
    assert len(picked) == 2
    assert picked[0]["v"] == 9


def test_sanitize_applies_tcvn3():
    from project_core.text.tcvn3 import tcvn3_to_unicode

    raw = "C©n ®èi"
    assert sanitize_sample_value("REMARK", raw) == tcvn3_to_unicode(raw)
    assert sanitize_sample_value("REMARK", raw) != raw


def test_normalize_shard_names():
    assert normalize_sample_table_key("STRANS_202607") == "STRANS"
    assert normalize_sample_table_key("dbo.PMTRANS_202401") == "PMTRANS"
    assert normalize_sample_table_key("TRANSHDR_ARC") == "TRANSHDR_ARC"
    assert normalize_sample_table_key("SKU_DEF") == "SKU_DEF"


def test_load_table_samples_from_repo_assets():
    samples = load_table_samples(["STRANS", "SKU_DEF"], allowed_tables=["STRANS", "SKU_DEF", "TRANSHDR"])
    assert len(samples) == 2
    assert samples[0]["table"].upper() == "STRANS"
    assert samples[0].get("error") is None
    assert samples[0]["row_count"] == 5
    assert len(samples[0]["rows"]) == 5


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
