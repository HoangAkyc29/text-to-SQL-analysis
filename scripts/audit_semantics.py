#!/usr/bin/env python3
"""Audit table/column semantics in data_dictionary against TOP-20 samples."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "docs" / "db_exploration_samples" / "samples_top20.json"
SHARDS = ROOT / "data_dictionary" / "db1" / "shards.yaml"

# Map logical dictionary table -> sample table name in db1 export
DB1_SAMPLE_ALIASES = {
    "STRANS": "STRANS_202504",
    "PMTRANS": "PMTRANS_202504",
    "CRDTRANS_ARC": "CRDTRANS_ARC",
    "TRANSHDR_ARC": "TRANSHDR_ARC",
}

# Columns we expect to validate semantically (not generic "Cột X")
KEY_CHECKS: dict[str, list[tuple[str, str]]] = {
    # table -> [(column, expected_pattern_or_hint)]
    "STRANS": [
        ("TRANS_CODE", "113"),
        ("AMOUNT", "numeric"),
        ("QTY", "numeric"),
        ("SKU_ID", "id"),
        ("STK_ID", "store"),
    ],
    "PMTRANS": [
        ("TRANS_CODE", "221|008"),
        ("PMT_CODE", "CASH|CARD|BANK"),
        ("AMOUNT", "numeric"),
    ],
    "TRANSHDR": [
        ("TRANS_CODE", "113"),
        ("AMOUNT", "numeric"),
        ("CUST_ID", "optional"),
    ],
    "TRANSHDR_ARC": [
        ("TRANS_CODE", "113"),
        ("AMOUNT", "numeric"),
    ],
    "CRDTRANS": [
        ("TRANS_CODE", "811"),
        ("CARD_ID", "card"),
        ("MARK", "points"),
    ],
    "CRDTRANS_ARC": [
        ("TRANS_CODE", "812"),
        ("CARD_ID", "card"),
    ],
    "CSCARD": [
        ("CARD_ID", "card"),
        ("DISC_LVL", "tier"),
    ],
    "CUSTOMER": [
        ("CUST_ID", "id"),
    ],
    "SKU_DEF": [
        ("SKU_ID", "id"),
        ("RTPRICE", "price"),
    ],
    "WebRpt_sales_sku_daily": [
        ("revenue", "numeric"),
        ("qty", "numeric"),
        ("report_date", "date"),
    ],
    "WebRpt_rfm_snapshot": [
        ("rfm_segment", "segment"),
        ("rfm_score", "numeric"),
    ],
    "SUSPEND": [
        ("TRANS_CODE", "221"),
    ],
    "PMCRDISS": [
        ("TRANS_CODE", "821"),
    ],
    "CASH_ST": [
        ("TRANS_CODE", "010"),
    ],
}


def load_samples() -> dict[str, dict[str, dict]]:
    data = json.loads(SAMPLES.read_text(encoding="utf-8"))
    out: dict[str, dict[str, dict]] = {"db1": {}, "db2": {}}
    for db in data["databases"]:
        key = "db1" if "db1" in db["db"] else "db2"
        for t in db["tables"]:
            if t.get("status") == "ok":
                out[key][t["table"]] = t
    return out


def parse_md(md_path: Path) -> tuple[dict, dict[str, str]]:
    text = md_path.read_text(encoding="utf-8")
    fm: dict = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            loaded = yaml.safe_load(text[3:end])
            fm = loaded if isinstance(loaded, dict) else {}
    cols: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("|") and not line.startswith("|--"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0].lower() not in {"column", "cột"}:
                cols[parts[0]] = parts[2]
    return fm, cols


def col_values(rows: list[dict], col: str) -> list:
    return [r[col] for r in rows if col in r and r[col] is not None]


def is_generic(desc: str) -> bool:
    return desc.startswith("Cột ")


def check_mark_amount_ratio(rows: list[dict]) -> str | None:
  rows811 = [r for r in rows if str(r.get("TRANS_CODE", "")).strip() in ("811", "812") and r.get("AMOUNT") and r.get("MARK")]
  if not rows811:
    return None
  ratios = []
  for r in rows811[:10]:
    try:
      amt = float(r["AMOUNT"])
      mark = float(r["MARK"])
      if mark > 0:
        ratios.append(amt / mark)
    except (TypeError, ValueError):
      pass
  if not ratios:
    return None
  avg = sum(ratios) / len(ratios)
  return f"AMOUNT/MARK avg≈{avg:,.0f} (n={len(ratios)})"


def audit_table(logical: str, sample: dict, fm: dict, col_desc: dict[str, str]) -> dict:
    rows = sample.get("rows", [])
    findings: list[str] = []
    confirms: list[str] = []
    gaps: list[str] = []

    desc = fm.get("description", "")
    if not rows:
        findings.append("Không có sample rows")
        return {"findings": findings, "confirms": confirms, "gaps": gaps}

    # Table-level TRANS_CODE check
    if "TRANS_CODE" in sample.get("columns", []):
        codes = sorted({str(v).strip() for v in col_values(rows, "TRANS_CODE")})
        if logical in ("STRANS", "TRANSHDR", "TRANSHDR_ARC") and "113" not in codes and codes != [""]:
            findings.append(f"TRANS_CODE mẫu {codes} — mô tả 'bán lẻ 113' có thể không luôn đúng")
        elif logical in ("STRANS", "TRANSHDR", "TRANSHDR_ARC") and "113" in codes:
            confirms.append(f"TRANS_CODE=113 có trong mẫu — khớp 'bán lẻ'")

    if logical == "PMTRANS":
        codes = sorted({str(v).strip() for v in col_values(rows, "TRANS_CODE")})
        pmts = sorted({str(v).strip() for v in col_values(rows, "PMT_CODE")}) if "PMT_CODE" in sample.get("columns", []) else []
        if codes:
            confirms.append(f"TRANS_CODE mẫu: {codes}")
        if pmts:
            confirms.append(f"PMT_CODE mẫu: {pmts}")
        if "221" in desc and "008" not in str(codes) and "008" not in desc:
            gaps.append("Mô tả chưa nhắc TRANS_CODE=008 (quỹ) nếu mẫu chỉ có 221")

    if logical in ("CRDTRANS", "CRDTRANS_ARC"):
        codes = sorted({str(v).strip() for v in col_values(rows, "TRANS_CODE")})
        expected = "811" if logical == "CRDTRANS" else "812"
        if expected in codes:
            confirms.append(f"TRANS_CODE={expected} trong mẫu — khớp loyalty")
        ratio = check_mark_amount_ratio(rows)
        if ratio:
            confirms.append(ratio)

    # AMOUNT=0 on STRANS (gift lines)
    if logical == "STRANS" and "AMOUNT" in sample.get("columns", []):
        zeros = sum(1 for r in rows if r.get("AMOUNT") in (0, 0.0, "0"))
        if zeros:
            confirms.append(f"{zeros}/{len(rows)} dòng AMOUNT=0 — khớp ghi chú 'quà/KM'")

    # Generic column descriptions count
    generic = [c for c, d in col_desc.items() if d.startswith("Cột ")]
    if generic:
        gaps.append(f"{len(generic)} cột mô tả generic (Cột X): {generic[:8]}{'...' if len(generic)>8 else ''}")

    # Check key column descriptions exist and non-generic
    for col, _ in KEY_CHECKS.get(logical, []):
        if col not in col_desc:
            gaps.append(f"Thiếu mô tả cột {col}")
        elif col_desc[col].startswith("Cột "):
            gaps.append(f"Cột quan trọng {col} vẫn generic")

    # WebRpt sanity
    if logical == "WebRpt_sales_sku_daily":
        if rows and "revenue" in rows[0] and "qty" in rows[0]:
            confirms.append("Có revenue/qty — khớp báo cáo doanh thu SKU/ngày")

    if logical == "WebRpt_rfm_snapshot":
        segs = sorted({str(r.get("rfm_segment", "")).strip() for r in rows if r.get("rfm_segment")})
        if segs:
            confirms.append(f"rfm_segment mẫu: {segs[:10]}")

    if logical == "SUSPEND":
        confirms.append("Bill treo — TRANS_CODE 221 trong mẫu khớp thanh toán chưa hoàn tất")

    if logical == "SKU_DEF":
        if any(r.get("RTPRICE") for r in rows):
            confirms.append("RTPRICE có giá trị — master giá bán lẻ")

    return {"findings": findings, "confirms": confirms, "gaps": gaps, "sample_table": sample.get("table")}


def main() -> None:
    if not SAMPLES.exists():
        print("Run explore_db_samples.py first", file=sys.stderr)
        sys.exit(1)

    samples = load_samples()
    report: dict = {"tables": {}, "summary": {"confirmed": 0, "findings": 0, "gaps": 0}}

    # db1 logical tables
    for logical, sample_name in DB1_SAMPLE_ALIASES.items():
        md = ROOT / "data_dictionary" / "tables" / "db1" / f"{logical}.md"
        if not md.exists() or sample_name not in samples["db1"]:
            report["tables"][f"db1:{logical}"] = {"error": "missing md or sample"}
            continue
        fm, cols = parse_md(md)
        result = audit_table(logical, samples["db1"][sample_name], fm, cols)
        report["tables"][f"db1:{logical}"] = result
        report["summary"]["confirmed"] += len(result.get("confirms", []))
        report["summary"]["findings"] += len(result.get("findings", []))
        report["summary"]["gaps"] += len(result.get("gaps", []))

    # db2 tables
    for md in sorted((ROOT / "data_dictionary" / "tables" / "db2").glob("*.md")):
        logical = md.stem
        if logical not in samples["db2"]:
            report["tables"][f"db2:{logical}"] = {"error": "no sample"}
            continue
        fm, cols = parse_md(md)
        result = audit_table(logical, samples["db2"][logical], fm, cols)
        report["tables"][f"db2:{logical}"] = result
        report["summary"]["confirmed"] += len(result.get("confirms", []))
        report["summary"]["findings"] += len(result.get("findings", []))
        report["summary"]["gaps"] += len(result.get("gaps", []))

    out = ROOT / "docs" / "db_exploration_samples" / "semantic_audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", out)
    print("Summary:", report["summary"])


if __name__ == "__main__":
    main()
