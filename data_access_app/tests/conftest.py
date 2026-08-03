"""Shared fixtures and query-capture helpers for domain tests (no live ODBC)."""
from __future__ import annotations

from datetime import date
from typing import Any, Callable

import pandas as pd
import pytest

from app.domain.columns import POINTS_DIVISOR, PRODUCT_COLUMNS, points_from_value


@pytest.fixture
def as_of() -> date:
    return date(2026, 7, 27)


@pytest.fixture
def range_ab() -> tuple[date, date]:
    """Date range entirely in db2 for typical July-2026 session clock."""
    return date(2026, 6, 10), date(2026, 7, 20)


@pytest.fixture
def card_profiles() -> pd.DataFrame:
    """CSCARD-like rows for filter / enrich tests."""
    return pd.DataFrame(
        {
            "CARD_ID": ["E10000000053", "A10000054973", "E10000000099", "B10000000001"],
            "NAME_U": ["Alice", "Bob", "Carol", "Dan"],
            "NAME": ["Alice", "Bob", "Carol", "Dan"],
            "PHONE": ["0901", "0902", "0903", "0904"],
            "MOBI": ["", "", "", ""],
            "SEX": ["F", "M", "F", "1"],  # 1 → M via normalize
            "BIRTHDAY": [
                "1990-07-15",  # age ~36 as of 2026-07-27, month 7
                "1985-01-20",  # age ~41, month 1
                "1995-07-01",  # age ~31, month 7
                "2000-12-31",  # age ~25, month 12
            ],
            "DISC_LVL": ["1", "2", "1", "3"],
            "CUST_ID": ["c1", "c2", "c3", "c4"],
        }
    )


@pytest.fixture
def sku_catalog() -> pd.DataFrame:
    rows = [
        {
            "SKU_ID": "1001",
            "SKU_CODE": "SP001",
            "BARCODE": "89001",
            "FULL_NAME_U": "Sữa tươi",
            "GRP_ID": "G1",
            "GRP_NAME": "Sữa",
            "DEPT_ID": "D1",
            "UNIT_SYMB": "HOP",
            "RTPRICE": 30000,
            "STATUS": "A",
        },
        {
            "SKU_ID": "1002",
            "SKU_CODE": "SP002",
            "BARCODE": "89002",
            "FULL_NAME_U": "Bánh quy",
            "GRP_ID": "G2",
            "GRP_NAME": "Bánh",
            "DEPT_ID": "D1",
            "UNIT_SYMB": "GOI",
            "RTPRICE": 20000,
            "STATUS": "A",
        },
        {
            "SKU_ID": "2001",
            "SKU_CODE": "QT001",
            "BARCODE": "89003",
            "FULL_NAME_U": "Quà tặng mẫu",
            "GRP_ID": "G9",
            "GRP_NAME": "Quà",
            "DEPT_ID": "D9",
            "UNIT_SYMB": "CAI",
            "RTPRICE": 0,
            "STATUS": "A",
        },
    ]
    return pd.DataFrame(rows)[PRODUCT_COLUMNS]


class QueryCapture:
    """Record query_strans / query_transhdr / master_select calls and return canned frames."""

    def __init__(self) -> None:
        self.strans_calls: list[dict[str, Any]] = []
        self.transhdr_calls: list[dict[str, Any]] = []
        self.master_calls: list[dict[str, Any]] = []
        self._strans_fn: Callable[..., pd.DataFrame] | None = None
        self._transhdr_fn: Callable[..., pd.DataFrame] | None = None
        self._master_fn: Callable[..., pd.DataFrame] | None = None

    def set_strans(self, fn: Callable[..., pd.DataFrame]) -> None:
        self._strans_fn = fn

    def set_transhdr(self, fn: Callable[..., pd.DataFrame]) -> None:
        self._transhdr_fn = fn

    def set_master(self, fn: Callable[..., pd.DataFrame]) -> None:
        self._master_fn = fn

    def query_strans(
        self,
        date_start,
        date_end,
        select_sql_body: str,
        *,
        extra_where: str = "",
        extra_params: list | None = None,
        sql_suffix: str = "",
        progress=None,
    ) -> pd.DataFrame:
        self.strans_calls.append(
            {
                "date_start": date_start,
                "date_end": date_end,
                "body": select_sql_body,
                "extra_where": extra_where or "",
                "extra_params": list(extra_params or []),
                "sql_suffix": sql_suffix or "",
            }
        )
        if self._strans_fn is None:
            return pd.DataFrame()
        return self._strans_fn(
            date_start,
            date_end,
            select_sql_body,
            extra_where=extra_where,
            extra_params=extra_params,
            sql_suffix=sql_suffix,
        )

    def query_transhdr(
        self,
        date_start,
        date_end,
        select_sql_body: str,
        *,
        extra_where: str = "",
        extra_params: list | None = None,
        sql_suffix: str = "",
        progress=None,
    ) -> pd.DataFrame:
        self.transhdr_calls.append(
            {
                "date_start": date_start,
                "date_end": date_end,
                "body": select_sql_body,
                "extra_where": extra_where or "",
                "extra_params": list(extra_params or []),
                "sql_suffix": sql_suffix or "",
            }
        )
        if self._transhdr_fn is None:
            return pd.DataFrame()
        return self._transhdr_fn(
            date_start,
            date_end,
            select_sql_body,
            extra_where=extra_where,
            extra_params=extra_params,
            sql_suffix=sql_suffix,
        )

    def master_select(self, sql: str, params: list | None = None) -> pd.DataFrame:
        self.master_calls.append({"sql": sql, "params": list(params or [])})
        if self._master_fn is None:
            return pd.DataFrame()
        return self._master_fn(sql, params)


def assert_where_contains(extra_where: str, *needles: str) -> None:
    low = (extra_where or "").upper().replace(" ", "")
    for n in needles:
        assert n.upper().replace(" ", "") in low, f"missing {n!r} in {extra_where!r}"


def assert_where_not_contains(extra_where: str, *needles: str) -> None:
    low = (extra_where or "").upper().replace(" ", "")
    for n in needles:
        assert n.upper().replace(" ", "") not in low, f"unexpected {n!r} in {extra_where!r}"


def make_lookup(profiles: pd.DataFrame) -> Callable[[list[str]], pd.DataFrame]:
    def _lookup(ids: list[str]) -> pd.DataFrame:
        want = {str(i).strip() for i in ids}
        return profiles.loc[profiles["CARD_ID"].astype(str).isin(want)].copy()

    return _lookup


def points_of(total_value: float) -> float:
    return points_from_value(total_value)
