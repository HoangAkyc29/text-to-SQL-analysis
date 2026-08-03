"""Unit tests for form validation helpers (no Flet UI)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.ui.validate import (
    card_prefix_value,
    line_looks_like_card_list,
    looks_like_card_id,
    parse_birth_month,
    split_tokens,
)


def test_card_id_shape():
    assert looks_like_card_id("E10000000053")
    assert looks_like_card_id("A10000054973")
    assert not looks_like_card_id("abc")
    assert not looks_like_card_id("bánh mì")


def test_line_looks_like_card_list():
    assert line_looks_like_card_list("E10000000053 A10000054973")
    assert line_looks_like_card_list("E10000000053,A10000054973")
    assert not line_looks_like_card_list("bánh mì hoa cúc")
    assert not line_looks_like_card_list("E10000000053")


def test_split_tokens_card_list_and_products():
    cards = split_tokens("E10000000053\nA10000054973")
    assert cards == ["E10000000053", "A10000054973"]
    # space-separated cards on one line
    assert split_tokens("E10000000053 A10000054973") == ["E10000000053", "A10000054973"]
    # product name with spaces stays one token
    assert split_tokens("bánh mì hoa cúc") == ["bánh mì hoa cúc"]


def test_card_prefix_value_ignores_stale_text_on_none():
    """Regression: __none__ + text='2' must NOT become prefix (zeros birth-month search)."""
    field = SimpleNamespace(value="__none__", text="2")
    assert card_prefix_value(field) == ""
    field2 = SimpleNamespace(value="__none__", text="(không lọc)")
    assert card_prefix_value(field2) == ""
    field3 = SimpleNamespace(value="E", text="whatever")
    assert card_prefix_value(field3) == "E"
    assert card_prefix_value(None) == ""


def test_validate_card_prefix_rejects_digit_only():
    from app.ui.validate import clear_errors, validate_card_prefix

    field = SimpleNamespace(value="2", text="2", error_text=None, border_color=None, focused_border_color=None)
    # validate_card_prefix uses set_error which needs more attrs — stub lightly
    class _F:
        def __init__(self, value):
            self.value = value
            self.error_text = None
            self.border_color = None
            self.focused_border_color = None

    f = _F("2")
    assert validate_card_prefix(f) is None
    assert f.error_text
    f2 = _F("E")
    assert validate_card_prefix(f2) == "E"
    f3 = _F("__none__")
    assert validate_card_prefix(f3) == ""


def test_parse_birth_month():
    assert parse_birth_month(None) is None
    assert parse_birth_month("any") is None
    assert parse_birth_month("2") == 2
    assert parse_birth_month("Tháng 2") == 2
    assert parse_birth_month("Tháng 12") == 12
    with pytest.raises(ValueError):
        parse_birth_month("Tháng 99")
    with pytest.raises(ValueError):
        parse_birth_month("abc")
