"""F1/F6 product search + token resolve."""
from __future__ import annotations

import pandas as pd
import pytest

from app.domain.columns import PRODUCT_COLUMNS
from app.domain.product import resolve_product_tokens, search_by_group, search_products
from app.domain.search_opts import SearchOpts, mark_truncated


def test_search_products_requires_code_or_name():
    with pytest.raises(ValueError, match="mã hoặc tên"):
        search_products()


def test_search_products_code_or_across_columns(monkeypatch, sku_catalog):
    seen = {}

    def fake_master(sql, params=None):
        seen["sql"] = sql
        seen["params"] = list(params or [])
        return sku_catalog.copy()

    monkeypatch.setattr("app.domain.product.master_select", fake_master)
    out = search_products(code="SP001")
    assert "SKU_CODE" in seen["sql"] and "BARCODE" in seen["sql"]
    assert "SKU_ID" in seen["sql"]
    assert len(seen["params"]) == 3  # 3 code columns
    assert list(out.columns) == PRODUCT_COLUMNS
    assert not out.empty


def test_search_products_code_and_name(monkeypatch, sku_catalog):
    seen = {}

    def fake_master(sql, params=None):
        seen["sql"] = sql
        seen["params"] = list(params or [])
        return sku_catalog.iloc[:1].copy()

    monkeypatch.setattr("app.domain.product.master_select", fake_master)
    search_products(code="SP001", name="Sữa")
    assert " AND " in seen["sql"]
    assert len(seen["params"]) == 4  # 3 code + 1 name


def test_search_by_group(monkeypatch, sku_catalog):
    seen = {}

    def fake_master(sql, params=None):
        seen["sql"] = sql
        return sku_catalog.copy()

    monkeypatch.setattr("app.domain.product.master_select", fake_master)
    out = search_by_group(group_code="G1")
    assert "GRP_ID" in seen["sql"]
    assert "ORDER BY GRP_ID" in seen["sql"]
    assert not out.empty


def test_resolve_tokens_union_code_and_name(monkeypatch, sku_catalog):
    def fake_search(*, code="", name="", limit=None, search=None):
        if code == "SP001":
            return sku_catalog.iloc[[0]].copy()
        if name == "Bánh":
            return sku_catalog.iloc[[1]].copy()
        return pd.DataFrame(columns=PRODUCT_COLUMNS)

    monkeypatch.setattr("app.domain.product.search_products", fake_search)
    out = resolve_product_tokens(["SP001", "Bánh", "  ", "UNKNOWN"])
    assert set(out["SP001"]["SKU_ID"]) == {"1001"}
    assert set(out["Bánh"]["SKU_ID"]) == {"1002"}
    assert out["UNKNOWN"].empty
    assert "  " not in out


def test_resolve_tokens_raises_on_truncate(monkeypatch, sku_catalog):
    def fake_search(*, code="", name="", limit=None, search=None):
        df = sku_catalog.copy()
        return mark_truncated(df, limit=1)  # force truncated attr

    monkeypatch.setattr("app.domain.product.search_products", fake_search)
    with pytest.raises(ValueError):
        resolve_product_tokens(["SP001"])


def test_exact_search_opts_uses_equality(monkeypatch, sku_catalog):
    seen = {}

    def fake_master(sql, params=None):
        seen["sql"] = sql
        seen["params"] = list(params or [])
        return sku_catalog.iloc[:1].copy()

    monkeypatch.setattr("app.domain.product.master_select", fake_master)
    search_products(code="SP001", search=SearchOpts(case_insensitive=False, fuzzy=False))
    assert "LIKE" not in seen["sql"].upper()
    assert seen["params"] == ["SP001", "SP001", "SP001"]
