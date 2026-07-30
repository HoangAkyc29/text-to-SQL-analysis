"""Unit tests for client-side result sorting."""
from __future__ import annotations

import pandas as pd

from app.domain.frame_sort import ResultSort, lead_and_sort


def test_lead_column_first():
    df = pd.DataFrame({"STK_ID": ["1"], "TRANS_NUM": ["T1"], "CARD_ID": ["E1"]})
    out = lead_and_sort(df, lead="TRANS_NUM", column="TRANS_NUM", ascending=True)
    assert list(out.columns)[:1] == ["TRANS_NUM"]


def test_sort_ascending_descending():
    df = pd.DataFrame({"TRANS_NUM": ["B", "A", "C"], "X": [1, 2, 3]})
    asc = lead_and_sort(df, lead="TRANS_NUM", column="TRANS_NUM", ascending=True)
    assert list(asc["TRANS_NUM"]) == ["A", "B", "C"]
    desc = lead_and_sort(df, lead="TRANS_NUM", column="TRANS_NUM", ascending=False)
    assert list(desc["TRANS_NUM"]) == ["C", "B", "A"]


def test_result_sort_toggle_and_sync():
    sort = ResultSort(lead="CARD_ID")
    df = pd.DataFrame({"CARD_ID": ["E2", "E1"], "points": [1, 9]})
    sort.sync_column_if_needed(df)
    out = sort.apply(df)
    assert list(out["CARD_ID"]) == ["E1", "E2"]
    sort.toggle_column("CARD_ID")
    out2 = sort.apply(df)
    assert list(out2["CARD_ID"]) == ["E2", "E1"]
    sort.set_column("points")
    out3 = sort.apply(df)
    assert list(out3["points"]) == [1, 9]
