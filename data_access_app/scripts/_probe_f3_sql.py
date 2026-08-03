"""Reproduce F3 STRANS query that failed in UI."""
from __future__ import annotations

import traceback
from datetime import date

from app.domain.loyalty_customers import fetch_loyalty_customers
from app.db.cutoff import split_date_range, rolling_cutoff
from app.db.session_clock import bootstrap_session_clock, status
from app.db.dual_query import query_strans
from app.domain.columns import BILL_VALUE_SQL


def main() -> None:
    bootstrap_session_clock()
    print("clock", status())
    print("cutoff", rolling_cutoff())
    # Typical UI default range — use recent window around as-of
    start, end = date(2026, 6, 1), date(2026, 7, 27)
    split = split_date_range(start, end)
    print("split", split.needs_db1, split.needs_db2, split.strans_shards[:3], "...", len(split.strans_shards))

    body = f"""
        SELECT
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            {BILL_VALUE_SQL} AS line_total
        FROM {{table}}
        WHERE 1=1
    """
    stores = ["10001", "10004", "10005"]
    ph = ",".join("?" for _ in stores)
    extra = (
        "CARD_ID IS NOT NULL AND LTRIM(RTRIM(CARD_ID)) <> '' "
        f"AND LTRIM(RTRIM(STK_ID)) IN ({ph})"
    )
    try:
        df = query_strans(start, end, body, extra_where=extra, extra_params=stores)
        print("query_strans rows", len(df))
    except Exception:
        traceback.print_exc()

    try:
        out = fetch_loyalty_customers(
            start,
            end,
            store_ids=stores,
            sex="M",
        )
        print("fetch_loyalty rows", len(out))
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
