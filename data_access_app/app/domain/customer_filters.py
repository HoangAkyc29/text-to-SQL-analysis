"""Filter order/line frames by CSCARD customer attributes (age, sex, card prefix)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

import pandas as pd

from app.domain.customer import lookup_cards
from app.domain.search_opts import DEFAULT_SEARCH, SearchOpts
from app.export.txt_report import age_years

SexFilter = Literal["any", "M", "F"]


def customer_filters_active(
    *,
    min_age: float | None = None,
    max_age: float | None = None,
    sex: SexFilter = "any",
    card_prefix: str = "",
) -> bool:
    return (
        min_age is not None
        or max_age is not None
        or (sex and sex != "any")
        or bool((card_prefix or "").strip())
    )


def _normalize_sex_token(val) -> str:
    raw = str(val or "").strip()
    s = raw.upper()
    if s in {"M", "1", "NAM", "MALE", "TRUE", "YES"}:
        return "M"
    if s in {"F", "0", "2", "NU", "FEMALE", "NO"} or raw.lower() in {"nữ", "nu"}:
        return "F"
    return s


def filter_frame_by_customer(
    df: pd.DataFrame,
    *,
    min_age: float | None = None,
    max_age: float | None = None,
    sex: SexFilter = "any",
    card_prefix: str = "",
    as_of: date | None = None,
    search: SearchOpts = DEFAULT_SEARCH,
) -> pd.DataFrame:
    """
    Keep rows whose CARD_ID passes CSCARD filters.
    Rows without CARD_ID are dropped when any filter is active.
    """
    if df is None or df.empty:
        return df
    if not customer_filters_active(
        min_age=min_age, max_age=max_age, sex=sex, card_prefix=card_prefix
    ):
        return df
    if "CARD_ID" not in df.columns:
        return df.iloc[0:0].copy()

    work = df.copy()
    work["_card"] = work["CARD_ID"].astype(str).str.strip()
    work = work.loc[work["_card"].ne("") & work["_card"].str.lower().ne("nan")]
    if work.empty:
        return work.drop(columns=["_card"], errors="ignore")

    prefix = (card_prefix or "").strip()
    if prefix:
        opts = search or DEFAULT_SEARCH
        if opts.case_insensitive:
            work = work.loc[work["_card"].str.lower().str.startswith(prefix.lower())]
        else:
            work = work.loc[work["_card"].str.startswith(prefix)]
        if work.empty:
            return work.drop(columns=["_card"], errors="ignore")

    need_profile = min_age is not None or max_age is not None or (sex and sex != "any")
    if need_profile:
        cards = lookup_cards(work["_card"].unique().tolist())
        if cards.empty:
            return work.iloc[0:0].drop(columns=["_card"], errors="ignore")
        prof = cards.copy()
        prof["CARD_ID"] = prof["CARD_ID"].astype(str).str.strip()
        if "BIRTHDAY" in prof.columns:
            ref = datetime.combine(as_of or date.today(), datetime.min.time())
            prof["_age"] = prof["BIRTHDAY"].map(lambda b: age_years(b, as_of=ref))
        else:
            prof["_age"] = None
        if "SEX" in prof.columns:
            prof["_sex"] = prof["SEX"].map(_normalize_sex_token)
        else:
            prof["_sex"] = ""

        mask = pd.Series(True, index=prof.index)
        if min_age is not None:
            mask &= prof["_age"].notna() & (prof["_age"] >= float(min_age))
        if max_age is not None:
            mask &= prof["_age"].notna() & (prof["_age"] <= float(max_age))
        if sex and sex != "any":
            mask &= prof["_sex"] == sex.upper()
        ok_ids = set(prof.loc[mask, "CARD_ID"].tolist())
        work = work.loc[work["_card"].isin(ok_ids)]

    return work.drop(columns=["_card"], errors="ignore")
