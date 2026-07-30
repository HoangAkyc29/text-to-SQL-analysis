"""Unit tests for SearchOpts SQL helpers."""
from __future__ import annotations

from app.domain.search_opts import (
    SearchOpts,
    bind_prefix,
    bind_value,
    expand_params,
    match_any,
    match_column,
    match_prefix_column,
)


def test_default_fuzzy_and_case():
    opts = SearchOpts()
    assert opts.case_insensitive and opts.fuzzy
    assert bind_value("  AbC  ", opts) == "%abc%"
    sql = match_column("SKU_CODE", opts)
    assert "LOWER(" in sql and "LIKE ?" in sql


def test_exact_case_sensitive():
    opts = SearchOpts(case_insensitive=False, fuzzy=False)
    assert bind_value("  AbC  ", opts) == "AbC"
    sql = match_column("CARD_ID", opts)
    assert "LOWER(" not in sql and "= ?" in sql


def test_match_any_expands_params():
    opts = SearchOpts()
    sql = match_any(["NAME_U", "NAME"], opts)
    assert " OR " in sql
    params = expand_params("Tea", 2, opts)
    assert params == ["%tea%", "%tea%"]


def test_prefix_starts_with_not_substring():
    opts = SearchOpts(case_insensitive=True, fuzzy=True)
    assert bind_prefix("E", opts) == "e%"
    assert bind_value("E", opts) == "%e%"
    assert "LIKE ?" in match_prefix_column("CARD_ID", opts)


def test_prefix_exact_when_fuzzy_off():
    opts = SearchOpts(case_insensitive=True, fuzzy=False)
    assert bind_prefix("E", opts) == "e"
    assert "= ?" in match_prefix_column("CARD_ID", opts)


def test_resolve_search_limit_from_settings(monkeypatch):
    from app.config import settings
    from app.domain.search_opts import resolve_search_limit

    monkeypatch.setattr(settings, "search_limit", 1234)
    assert resolve_search_limit() == 1234
    assert resolve_search_limit(10) == 10
