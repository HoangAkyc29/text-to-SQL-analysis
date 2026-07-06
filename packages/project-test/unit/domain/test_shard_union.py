"""db1 shard UNION SQL helper."""

from __future__ import annotations

import pytest

from project_core.domain.sql.shard_resolver import build_db1_union_sql

pytestmark = pytest.mark.unit


def test_build_db1_union_sql():
    base = "SELECT TOP 10 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"
    out = build_db1_union_sql(base, ["STRANS_202401", "STRANS_202402"])
    assert "STRANS_202401" in out
    assert "STRANS_202402" in out
    assert "UNION ALL" in out
    assert "STRANS WHERE" not in out
