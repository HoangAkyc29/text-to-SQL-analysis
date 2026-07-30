"""Focused live retest: F3 export + F4/F5 with known active card/SKU."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.db.dual_query import master_select, query_strans
from app.domain import customer_orders as co_svc
from app.domain import loyalty_customers as loyalty_svc
from app.domain import product_orders as po_svc
from app.export.splitters import parse_point_buckets


def main() -> int:
    settings.reload()
    out = settings.output_dir / "smoke_live2"
    out.mkdir(parents=True, exist_ok=True)
    start, end = date(2026, 5, 1), date.today()
    stores = ["10001", "10004", "10005"]
    failed = 0

    print("Discover active CARD_ID / SKU_ID from STRANS…")
    sample = query_strans(
        start,
        end,
        """
        SELECT TOP 20
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(SKU_ID)) AS SKU_ID,
            LTRIM(RTRIM(STK_ID)) AS STK_ID
        FROM {table}
        WHERE 1=1
        """,
        extra_where=(
            "CARD_ID IS NOT NULL AND LTRIM(RTRIM(CARD_ID)) <> '' "
            "AND SKU_ID IS NOT NULL "
            "AND LTRIM(RTRIM(STK_ID)) IN (?,?,?)"
        ),
        extra_params=stores,
    )
    print("sample lines", len(sample))
    if sample.empty:
        print("No STRANS sample — abort")
        return 1
    print(sample.head(5).to_string(index=False))
    card = str(sample.iloc[0]["CARD_ID"]).strip()
    sku = str(sample.iloc[0]["SKU_ID"]).strip()
    sku_code_df = master_select(
        "SELECT TOP 1 SKU_ID, SKU_CODE, FULL_NAME_U FROM SKU_DEF WHERE SKU_ID = ?",
        [sku],
    )
    token = str(sku_code_df.iloc[0]["SKU_CODE"]).strip() if not sku_code_df.empty else sku
    print(f"using card={card!r} sku={sku!r} token={token!r}")

    print("\n=== F3 export ===")
    try:
        df = loyalty_svc.fetch_loyalty_customers(
            start,
            end,
            card_prefix=card[:1],
            store_ids=stores,
            min_metric=0,
            progress=print,
        )
        # keep it smaller for export smoke
        df = df.head(200)
        paths = loyalty_svc.export_loyalty(
            df,
            out / "F3",
            date_start=start,
            date_end=end,
            store_ids=stores,
            buckets=parse_point_buckets("0-10,10-50,>50"),
            txt_options=["count", "by_points", "by_store"],
        )
        print("F3 OK files:", [p.name for p in paths], "rows", len(df))
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F3 FAIL", exc)

    print("\n=== F4 ===")
    try:
        df, seed_skus = co_svc.fetch_customer_orders(
            start,
            end,
            [card],
            store_ids=stores,
            gift_mode="any",
            progress=print,
        )
        print("F4 lines", len(df))
        if not df.empty:
            print(df.head(3).to_string(index=False))
            paths = co_svc.export_customer_orders(
                df,
                out / "F4",
                date_start=start,
                date_end=end,
                exclude_skus=seed_skus,
            )
            print("F4 OK files:", [p.name for p in paths])
        else:
            failed += 1
            print("F4 FAIL empty")
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F4 FAIL", exc)

    print("\n=== F5 ===")
    try:
        per, unresolved, seeds = po_svc.fetch_product_orders(
            start,
            end,
            [token],
            store_ids=stores,
            require_card=True,
            gift_mode="any",
            progress=print,
        )
        df = per.get(token)
        print("F5 unresolved", unresolved, "rows", 0 if df is None else len(df))
        paths = po_svc.export_product_orders(
            per,
            out / "F5",
            date_start=start,
            date_end=end,
            seed_skus_by_token=seeds,
            include_card_list=True,
            include_aggregate=False,
        )
        print("F5 OK files:", [p.name for p in paths])
        if df is None or df.empty:
            failed += 1
            print("F5 FAIL empty")
        else:
            print(df.head(3).to_string(index=False))
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F5 FAIL", exc)

    print("\nDONE failed=", failed, "out=", out)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
