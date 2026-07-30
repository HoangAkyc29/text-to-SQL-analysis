"""Live end-to-end smoke against DESKTOP-AUQEDC5 (readonly)."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.domain import customer as customer_svc
from app.domain import customer_orders as co_svc
from app.domain import loyalty_customers as loyalty_svc
from app.domain import product as product_svc
from app.domain import product_orders as po_svc
from app.export.splitters import parse_point_buckets


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> int:
    settings.reload()
    out = settings.output_dir / "smoke_live"
    out.mkdir(parents=True, exist_ok=True)
    end = date.today()
    # Prefer recent live window that still has traffic; include May for dual-db coverage.
    start = date(2026, 5, 1)
    if end < start:
        start = end - timedelta(days=45)
    stores = ["10001", "10004", "10005"]
    failed = 0

    # F1
    section("F1 search products")
    try:
        df = product_svc.search_products(code="00000001", limit=5)
        print(f"by code rows={len(df)} cols={list(df.columns)}")
        if not df.empty:
            print(df.head(2).to_string(index=False))
        df2 = product_svc.search_products(name="a", limit=5)
        print(f"by name LIKE 'a' rows={len(df2)}")
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F1 FAIL:", exc)

    # F6
    section("F6 products by group")
    try:
        # discover a GRP_ID first
        from app.db.dual_query import master_select

        g = master_select("SELECT TOP 1 GRP_ID, GRP_NAME FROM SKU_DEF WHERE GRP_ID IS NOT NULL")
        print("sample group:", g.to_string(index=False) if not g.empty else "(none)")
        if not g.empty:
            gid = str(g.iloc[0]["GRP_ID"]).strip()
            df = product_svc.search_by_group(group_code=gid, limit=10)
            print(f"group {gid!r} products={len(df)}")
            if not df.empty:
                print(df.head(2).to_string(index=False))
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F6 FAIL:", exc)

    # F2
    section("F2 search customers")
    try:
        df = customer_svc.search_customers(card_prefix="A", limit=5)
        print(f"prefix A rows={len(df)} cols={list(df.columns)}")
        if not df.empty:
            print(df[["CARD_ID", "NAME", "PHONE"]].head(3).to_string(index=False))
            sample_card = str(df.iloc[0]["CARD_ID"]).strip()
        else:
            sample_card = ""
            df_e = customer_svc.search_customers(card_prefix="E", limit=5)
            print(f"prefix E rows={len(df_e)}")
            if not df_e.empty:
                sample_card = str(df_e.iloc[0]["CARD_ID"]).strip()
                print(df_e[["CARD_ID", "NAME"]].head(2).to_string(index=False))
    except Exception as exc:  # noqa: BLE001
        failed += 1
        sample_card = ""
        print("F2 FAIL:", exc)

    # F3
    section(f"F3 loyalty customers {start} .. {end}")
    try:
        df = loyalty_svc.fetch_loyalty_customers(
            start,
            end,
            card_prefix="A",
            store_ids=stores,
            filter_mode="points",
            min_metric=0,
            progress=lambda m: print(" ", m),
        )
        print(f"customers={len(df)} cols={list(df.columns)}")
        if not df.empty:
            print(df.head(3).to_string(index=False))
            paths = loyalty_svc.export_loyalty(
                df.head(50),
                out / "F3",
                date_start=start,
                date_end=end,
                store_ids=stores,
                buckets=parse_point_buckets("0-10,10-50,>50"),
                txt_options=["count", "by_points", "by_store", "by_age"],
                meta={"from": str(start), "to": str(end)},
            )
            print("exported:", [p.name for p in paths])
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F3 FAIL:", exc)

    # F4
    section(f"F4 customer orders card={sample_card!r}")
    try:
        if not sample_card:
            print("SKIP — no sample card")
        else:
            df, seed_skus = co_svc.fetch_customer_orders(
                start,
                end,
                [sample_card],
                store_ids=stores,
                product_query="",
                min_bill=0,
                gift_mode="any",
                progress=lambda m: print(" ", m),
            )
            print(f"order lines={len(df)}")
            if not df.empty:
                print(df.head(3).to_string(index=False))
                paths = co_svc.export_customer_orders(
                    df,
                    out / "F4",
                    date_start=start,
                    date_end=end,
                    exclude_skus=seed_skus,
                )
                print("exported:", [p.name for p in paths])
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F4 FAIL:", exc)

    # F5
    section(f"F5 product orders {start} .. {end}")
    try:
        # use a real SKU_CODE from F1 if possible
        token = "00000001"
        per, unresolved, seeds = po_svc.fetch_product_orders(
            start,
            end,
            [token],
            store_ids=stores,
            require_card=True,
            min_bill=None,
            gift_mode="any",
            progress=lambda m: print(" ", m),
        )
        df = per.get(token)
        print(f"token={token!r} unresolved={unresolved} rows={0 if df is None else len(df)}")
        if df is not None and not df.empty:
            print(df.head(3).to_string(index=False))
        paths = po_svc.export_product_orders(
            per,
            out / "F5",
            date_start=start,
            date_end=end,
            seed_skus_by_token=seeds,
            include_aggregate=False,
            include_card_list=True,
        )
        print("exported:", [p.name for p in paths])
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print("F5 FAIL:", exc)

    section("DONE")
    print(f"failed={failed} output={out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
