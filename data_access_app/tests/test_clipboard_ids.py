"""Unit tests for clipboard ID extraction (no Flet/UI)."""
from __future__ import annotations

import pandas as pd

from app.ui.clipboard_ids import format_id_list, unique_column_values


def test_unique_column_values_order_and_dedupe():
    df = pd.DataFrame({"CARD_ID": ["A1", "A2", "A1", None, "  ", "A3", float("nan")]})
    assert unique_column_values(df, "CARD_ID") == ["A1", "A2", "A3"]


def test_unique_missing_column():
    df = pd.DataFrame({"X": [1]})
    assert unique_column_values(df, "CARD_ID") == []
    assert unique_column_values(None, "CARD_ID") == []
    assert unique_column_values(pd.DataFrame(), "CARD_ID") == []


def test_format_id_list_newlines():
    assert format_id_list(["E1", "E2"]) == "E1\nE2"
