#!/usr/bin/env python3
"""Extract semantic evidence from TOP-20 samples for manual review."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "docs" / "db_exploration_samples" / "samples_top20.json"
OUT = ROOT / "docs" / "db_exploration_samples" / "semantic_evidence.json"

DB1_MAP = {
    "STRANS": "STRANS_202504",
    "PMTRANS": "PMTRANS_202504",
    "CRDTRANS_ARC": "CRDTRANS_ARC",
    "TRANSHDR_ARC": "TRANSHDR_ARC",
}

FOCUS_COLS = {
    "STRANS": ["TRANS_CODE", "TRANS_NUM", "STK_ID", "SKU_ID", "QTY", "AMOUNT", "PRICE", "DISCOUNT", "CARD_ID", "POST"],
    "PMTRANS": ["TRANS_CODE", "PMT_CODE", "AMOUNT", "TRANS_NUM", "STK_ID", "CYS"],
    "TRANSHDR": ["TRANS_CODE", "TRANS_NUM", "AMOUNT", "CUST_ID", "STK_ID", "POST"],
    "TRANSHDR_ARC": ["TRANS_CODE", "TRANS_NUM", "AMOUNT", "CUST_ID", "STK_ID"],
    "CRDTRANS": ["TRANS_CODE", "CARD_ID", "AMOUNT", "MARK", "TRANS_NUM", "ACML_CODE"],
    "CRDTRANS_ARC": ["TRANS_CODE", "CARD_ID", "AMOUNT", "MARK", "TRANS_NUM"],
    "CSCARD": ["CARD_ID", "NAME", "DISC_LVL", "DISC_CODE", "CUST_ID"],
    "SKU_DEF": ["SKU_ID", "SKU_CODE", "RTPRICE", "SPPRICE", "GRP_ID", "SALEABLE"],
    "CTRANS": ["TRANS_CODE", "DEBT_NO", "AMOUNT", "ACCOUNT_ID", "BILL"],
    "ST_ORDER": ["TRANS_CODE", "ORD_QTY", "STK_ID", "SUPP_ID"],
    "INV_HDR": ["TRANS_CODE", "INV_NO", "SUPP_ID", "AMOUNT", "POST"],
    "CASH_ST": ["TRANS_CODE", "VALUE", "STK_ID", "SHIFT"],
    "SUSPEND": ["TRANS_CODE", "TRANS_NUM", "SKU_ID", "AMOUNT"],
    "WebRpt_sales_sku_daily": ["report_date", "stk_id", "sku_id", "qty", "revenue", "cogs", "gross_profit"],
    "WebRpt_rfm_snapshot": ["card_id", "rfm_segment", "rfm_score", "monetary", "recency_days"],
    "WebRpt_inventory_daily": ["report_date", "qty_onhand", "stock_status", "doi_days"],
    "RDISCINF": ["DISC_CODE", "DISC_LVL", "OBJ_VALUE", "CHG_TYPE"],
    "PMCRDISS": ["TRANS_CODE", "PREFIX", "FR_SERI", "TO_SERI"],
}


def parse_md(p: Path) -> tuple[str, dict[str, str]]:
    text = p.read_text(encoding="utf-8")
    desc = ""
    if text.startswith("---"):
        fm = yaml.safe_load(text.split("---")[1])
        desc = fm.get("description", "") if isinstance(fm, dict) else ""
    cols: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("|") and not line.startswith("|--"):
            parts = [x.strip() for x in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0].lower() not in ("column", "cột"):
                cols[parts[0]] = parts[2]
    return desc, cols


def profile_table(rows: list[dict], cols: list[str]) -> dict:
    prof: dict = {}
    for c in cols:
        if c not in (rows[0] if rows else {}):
            continue
        vals = [r[c] for r in rows if r.get(c) is not None and r.get(c) != ""]
        if not vals:
            prof[c] = {"empty": True}
            continue
        if isinstance(vals[0], (int, float)):
            prof[c] = {"min": min(vals), "max": max(vals), "sample": vals[:3]}
        else:
            ctr = Counter(str(v).strip() for v in vals)
            prof[c] = {"distinct": len(ctr), "top": ctr.most_common(8)}
    return prof


def main() -> None:
    data = json.loads(SAMPLES.read_text(encoding="utf-8"))
    db1 = {t["table"]: t for t in data["databases"][0]["tables"] if t["status"] == "ok"}
    db2 = {t["table"]: t for t in data["databases"][1]["tables"] if t["status"] == "ok"}
    report: dict = {}

    for logical, sample_name in DB1_MAP.items():
        md = ROOT / "data_dictionary" / "tables" / "db1" / f"{logical}.md"
        tdesc, cdesc = parse_md(md)
        rows = db1[sample_name]["rows"]
        focus = FOCUS_COLS.get(logical, [])
        report[f"db1:{logical}"] = {
            "table_description": tdesc,
            "sample_from": sample_name,
            "profile": profile_table(rows, focus),
            "column_desc_check": {c: cdesc.get(c, "MISSING") for c in focus if c in cdesc},
        }

    for md in sorted((ROOT / "data_dictionary" / "tables" / "db2").glob("*.md")):
        logical = md.stem
        if logical not in db2:
            continue
        tdesc, cdesc = parse_md(md)
        rows = db2[logical]["rows"]
        focus = FOCUS_COLS.get(logical, ["TRANS_CODE"] if "TRANS_CODE" in (rows[0] if rows else {}) else [])
        entry = {
            "table_description": tdesc,
            "profile": profile_table(rows, focus) if focus else profile_table(rows, list(rows[0].keys())[:10]),
        }
        if focus:
            entry["column_desc_check"] = {c: cdesc.get(c, "MISSING") for c in focus if c in cdesc}
        report[f"db2:{logical}"] = entry

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
