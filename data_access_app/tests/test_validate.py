"""Unit tests for form validation helpers (no Flet UI)."""
from __future__ import annotations

from app.ui.validate import (
    line_looks_like_card_list,
    looks_like_card_id,
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
