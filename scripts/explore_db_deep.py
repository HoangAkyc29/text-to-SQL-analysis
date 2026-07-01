#!/usr/bin/env python3
"""Deep read-only DB exploration (TOP 20 / table) — raw stats to db_exploration_samples/."""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.text.tcvn3 import tcvn3_to_unicode  # noqa: E402

MAX_ROWS = 20
OUT_SAMPLES = ROOT / "docs" / "db_exploration_samples"
RAW_REPORT_PATH = OUT_SAMPLES / "raw_per_table_exploration.md"

TEXT_HINTS = (
    "NAME", "DESCRIPT", "REMARK", "NOTES", "ADDR", "ADDRESS", "skuname", "stkname",
    "grpname", "stock_status", "rfm_segment", "TAX_NAME", "CUST_NAME", "SUPP_NAME",
)

CATEGORICAL_COLS = {
    "TRANS_CODE", "TRANS_TYPE", "PMT_CODE", "ACML_CODE", "TYPE", "POST", "ACTION",
    "STATUS", "RS_CODE", "INV_TYPE", "ISS_TYPE", "PMT_TYPE", "PMT_MODE", "CYS",
    "ASSO_TYPE", "ITEM_TYPE", "MERC_TYPE", "rfm_segment", "stock_status", "card_type",
}

NUMERIC_TYPES = {"numeric", "decimal", "int", "bit", "float", "real", "money", "smallint", "tinyint"}


def _json_default(obj: object) -> str:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return str(obj)


def load_schema(json_path: Path) -> dict[str, dict]:
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    return {
        t["table_name"]: {
            "record_count": t.get("record_count"),
            "columns": {c["column_name"]: c["data_type"] for c in t["columns"]},
        }
        for t in data
    }


def connect(dsn_env: str) -> pyodbc.Connection:
    dsn = os.getenv(dsn_env)
    if not dsn:
        raise RuntimeError(f"{dsn_env} not set")
    return pyodbc.connect(dsn, timeout=120)


def cell_str(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    return str(val)


def is_text_column(col: str, dtype: str) -> bool:
    d = dtype.lower()
    if d not in ("char", "varchar", "nvarchar", "ntext", "text"):
        return False
    cu = col.upper()
    return any(h in cu for h in TEXT_HINTS) or d in ("nvarchar", "ntext")


def sample_table(conn: pyodbc.Connection, table: str) -> dict[str, Any]:
    cur = conn.cursor()
    sql = f"SELECT TOP {MAX_ROWS} * FROM [{table}]"
    try:
        cur.execute(sql)
        columns = [c[0] for c in cur.description] if cur.description else []
        rows: list[dict[str, Any]] = []
        for row in cur.fetchall():
            rows.append({columns[i]: row[i] for i in range(len(columns))})
        return {"table": table, "status": "ok", "columns": columns, "rows": rows}
    except Exception as exc:  # noqa: BLE001
        return {"table": table, "status": "error", "error": str(exc)[:500]}


def analyze_table(
    table: str,
    schema: dict,
    sample: dict[str, Any],
) -> dict[str, Any]:
    if sample.get("status") != "ok":
        return {"table": table, "status": "error", "error": sample.get("error")}

    col_types = schema.get("columns", {})
    rows = sample["rows"]
    decoded_rows = []
    tcvn3_examples: list[dict[str, str]] = []

    for row in rows:
        dec = {}
        for k, v in row.items():
            raw = cell_str(v)
            conv = tcvn3_to_unicode(raw) if raw else raw
            dec[k] = conv
            if raw and conv != raw and len(tcvn3_examples) < 3:
                if is_text_column(k, col_types.get(k, "char")):
                    tcvn3_examples.append(
                        {"column": k, "raw": raw[:120], "decoded": conv[:120]}
                    )
        decoded_rows.append(dec)

    cat_stats: dict[str, list[str]] = {}
    num_stats: dict[str, dict[str, str]] = {}
    date_stats: dict[str, dict[str, str]] = {}

    for col in sample["columns"]:
        dtype = col_types.get(col, "").lower()
        vals = [r.get(col) for r in rows if r.get(col) is not None]
        if not vals:
            continue
        if col in CATEGORICAL_COLS or (dtype in ("char", "varchar") and col not in {
            "TRANS_NUM", "CARD_ID", "CUST_ID", "SKU_ID", "STK_ID", "BARCODE", "REF",
        }):
            stripped = sorted({cell_str(v).strip() for v in vals if cell_str(v).strip()})
            if 0 < len(stripped) <= 20:
                cat_stats[col] = stripped
            elif stripped:
                cat_stats[col] = stripped[:15] + [f"...+{len(stripped) - 15} more"]

        if dtype in NUMERIC_TYPES and col not in ("STATUS", "UPDATED"):
            try:
                nums = [float(v) for v in vals]
                num_stats[col] = {"min": str(min(nums)), "max": str(max(nums))}
            except (TypeError, ValueError):
                pass

        if "DATE" in col.upper() or col in ("report_date", "snapshot_date"):
            try:
                date_stats[col] = {
                    "min": _json_default(min(vals)),
                    "max": _json_default(max(vals)),
                }
            except TypeError:
                pass

    # loyalty points ratio
    mark_ratio = None
    if "AMOUNT" in sample["columns"] and "MARK" in sample["columns"]:
        ratios = []
        for r in rows:
            try:
                amt = float(r.get("AMOUNT") or 0)
                mark = float(r.get("MARK") or 0)
                if amt > 0 and mark > 0:
                    ratios.append(round(amt / mark))
            except (TypeError, ValueError):
                pass
        if ratios:
            mark_ratio = Counter(ratios).most_common(3)

    return {
        "table": table,
        "status": "ok",
        "schema_record_count": schema.get("record_count"),
        "sample_rows": len(rows),
        "categorical": cat_stats,
        "numeric_ranges": num_stats,
        "date_ranges": date_stats,
        "tcvn3_examples": tcvn3_examples,
        "mark_amount_ratio": mark_ratio,
        "decoded_rows": decoded_rows,
    }


def global_aggregates(all_tables: list[dict[str, Any]]) -> dict[str, Any]:
    trans_codes: Counter[str] = Counter()
    pmt_codes: Counter[str] = Counter()
    card_prefixes: Counter[str] = Counter()
    stk_ids: Counter[str] = Counter()
    shard_mismatch: list[str] = []
    pat = re.compile(r"^(STRANS|PMTRANS)_(\d{6})$")

    for t in all_tables:
        if t.get("status") != "ok":
            continue
        name = t["table"]
        for row in t.get("decoded_rows", []):
            if "TRANS_CODE" in row and row["TRANS_CODE"]:
                trans_codes[cell_str(row["TRANS_CODE"]).strip()] += 1
            if "PMT_CODE" in row and row["PMT_CODE"]:
                pmt_codes[cell_str(row["PMT_CODE"]).strip()] += 1
            if "CARD_ID" in row and row["CARD_ID"]:
                cid = cell_str(row["CARD_ID"]).strip()
                if cid:
                    card_prefixes[cid[0]] += 1
            if "STK_ID" in row and row["STK_ID"]:
                stk_ids[cell_str(row["STK_ID"]).strip()] += 1

        m = pat.match(name)
        if m:
            ym = m.group(2)
            for row in t.get("decoded_rows", []):
                td = row.get("TRAN_DATE")
                if td:
                    act = f"{td.year:04d}{td.month:02d}" if hasattr(td, "year") else str(td)[:7].replace("-", "")
                    if hasattr(td, "year"):
                        act = f"{td.year:04d}{td.month:02d}"
                    else:
                        act = str(td)[:4] + str(td)[5:7]
                    if act != ym:
                        shard_mismatch.append(f"{name}: sample has {act} vs shard {ym}")
                        break

    tcvn3_tables = [
        t["table"]
        for t in all_tables
        if t.get("status") == "ok" and t.get("tcvn3_examples")
    ]

    return {
        "trans_codes": trans_codes.most_common(25),
        "pmt_codes": pmt_codes.most_common(15),
        "card_prefixes": card_prefixes.most_common(10),
        "stk_ids": stk_ids.most_common(10),
        "shard_mismatches": shard_mismatch[:10],
        "tcvn3_affected_tables": tcvn3_tables,
    }


def logical_group(table: str) -> str:
    if table.startswith("WebRpt"):
        return "reporting"
    if re.match(r"^(STRANS|PMTRANS)_\d{6}$", table):
        return "db1_shard"
    if table in ("STRANS", "PMTRANS", "TRANSHDR", "CRDTRANS", "CTRANS", "CASH_ST"):
        return "transactions_live"
    if "_TMP" in table or table == "SUSPEND":
        return "staging"
    if table.startswith(("CRD", "CSCARD", "PMCRD")):
        return "loyalty"
    if table in ("CUSTOMER", "CUSTHIST", "CustSumm", "PARTNER", "SUPPLIER"):
        return "party_master"
    if table.startswith(("SKU", "PLU", "BARCODE", "ASSO")) or table == "sku_activity":
        return "product"
    if table.startswith(("STK", "INV", "ST_ORDER")):
        return "inventory_invoice"
    if table.startswith(("HIS", "RDISC")):
        return "pricing_promo"
    if table in ("ACCOUNT", "DEBT"):
        return "finance"
    if table.endswith("_ARC"):
        return "db1_archive"
    return "other"


def render_report(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Database Exploration Report",
        "",
        "Tài liệu tổng hợp khám phá **read-only** trên SQL Server local.",
        "",
        "## Phạm vi & giới hạn",
        "",
        f"- Server: `DESKTOP-AUQEDC5`",
        f"- **db1** `RESTORED_DB` — {payload['db1']['table_count']} bảng (từ JSON export)",
        f"- **db2** `RESTORED_DB2` — {payload['db2']['table_count']} bảng (từ JSON export)",
        f"- Mỗi bảng: `SELECT TOP {MAX_ROWS}` only",
        f"- User: `analysisagentreadonly` (readonly)",
        f"- Lỗi kết nối/query: db1={payload['db1']['errors']}, db2={payload['db2']['errors']}",
        "",
        "## Tóm tắt điều hành",
        "",
        "1. **db1** = archive giao dịch băm tháng (`STRANS_*`, `PMTRANS_*`) + 2 bảng archive (`*_ARC`).",
        "2. **db2** = master (KH, SKU, NCC), giao dịch live, staging (`SUSPEND`, `*_TMP`), báo cáo `WebRpt_*`.",
        "3. Schema **STRANS/PMTRANS/TRANSHDR/CRDTRANS** giống hệt giữa db1 shard/arc và db2 live.",
        "4. **`TRANS_CODE` 221** = thanh toán bán; **113** = bán lẻ (header+dòng); **008** = quỹ; **811/812/821** = thẻ/PM.",
        "5. **`PMT_CODE`**: CASH, CARD, BANK, OWNCP.",
        "6. **Điểm:** `AMOUNT/MARK ≈ 50,000` trên CRDTRANS.",
        "7. **Thẻ:** prefix `A`, `E`, `@P` (voucher PM); cửa hàng `STK_ID` chủ yếu `10001`, `10004`, `10005`.",
        "8. **TCVN3:** 40 bảng db1 + 19 bảng db2 có text cần decode — xem `project_core/text/tcvn3.py`.",
        "9. **Agent:** ưu tiên `WebRpt_*` cho aggregate; raw STRANS chỉ khi cần chi tiết.",
        "",
        "Tái tạo report: `python scripts/explore_db_deep.py`",
        "",
        "## TCVN3 → Unicode",
        "",
        "Nhiều cột text (đặc biệt `varchar`/`char`) lưu tiếng Việt theo **TCVN3** (ABC/VNI legacy),",
        "khi đọc qua ODBC có thể hiện mojibake. Report dùng bộ map chuẩn trong:",
        "`packages/project-core/src/project_core/text/tcvn3.py` (`tcvn3_to_unicode`).",
        "",
        "Sẽ cần expose thành tool/post-process cho SQL gateway / sandbox để output agent luôn Unicode.",
        "",
    ]

    for db_key, label in [("db1", "RESTORED_DB (db1)"), ("db2", "RESTORED_DB2 (db2)")]:
        db = payload[db_key]
        lines += [f"## {label}", ""]
        g = db["global"]
        lines += [
            "### Tổng hợp chéo bảng (từ mẫu)",
            "",
            "**TRANS_CODE** (tần suất trong mẫu):",
            "",
        ]
        for code, cnt in g["trans_codes"]:
            lines.append(f"- `{code}`: {cnt} dòng mẫu")
        lines += ["", "**PMT_CODE**:", ""]
        for code, cnt in g["pmt_codes"]:
            lines.append(f"- `{code}`: {cnt}")
        lines += ["", "**CARD_ID prefix** (ký tự đầu):", ""]
        for p, cnt in g["card_prefixes"]:
            lines.append(f"- `{p}`: {cnt}")
        lines += ["", "**STK_ID** (cửa hàng/kho, top mẫu):", ""]
        for s, cnt in g["stk_ids"][:8]:
            lines.append(f"- `{s}`: {cnt}")
        if g["shard_mismatches"]:
            lines += ["", "**Shard month mismatch** (mẫu vs tên bảng):", ""]
            for m in g["shard_mismatches"]:
                lines.append(f"- {m}")
        else:
            lines += ["", "**Shard month:** mẫu khớp suffix `_YYYYMM` (không phát hiện lệch).", ""]
        lines += [
            "",
            f"**Bảng có text TCVN3 cần decode** ({len(g['tcvn3_affected_tables'])}):",
            "",
        ]
        for tname in g["tcvn3_affected_tables"]:
            lines.append(f"- `{tname}`")
        lines.append("")

        # Group tables
        groups: dict[str, list[dict]] = defaultdict(list)
        for t in db["tables"]:
            groups[logical_group(t["table"])].append(t)

        lines += ["### Chi tiết theo nhóm", ""]
        for grp in sorted(groups):
            lines += [f"#### {grp}", ""]
            for t in sorted(groups[grp], key=lambda x: x["table"]):
                lines += [f"##### `{t['table']}`", ""]
                if t["status"] != "ok":
                    lines.append(f"- **Lỗi:** {t.get('error')}")
                    lines.append("")
                    continue
                rc = t.get("schema_record_count")
                lines.append(f"- Rows (metadata JSON): {rc:,}" if rc else "- Rows (metadata): ?")
                lines.append(f"- Mẫu lấy: {t['sample_rows']} dòng")

                if t.get("mark_amount_ratio"):
                    lines.append(f"- Tỷ lệ AMOUNT/MARK phổ biến (điểm): {t['mark_amount_ratio']}")

                if t.get("date_ranges"):
                    lines.append("- Khoảng ngày (mẫu):")
                    for dc, dr in list(t["date_ranges"].items())[:4]:
                        lines.append(f"  - `{dc}`: {dr['min']} → {dr['max']}")

                if t.get("categorical"):
                    lines.append("- Giá trị phân loại (mẫu):")
                    for col, vals in list(t["categorical"].items())[:8]:
                        vstr = ", ".join(f"`{v}`" for v in vals[:10])
                        lines.append(f"  - `{col}`: {vstr}")

                if t.get("numeric_ranges"):
                    interesting = {k: v for k, v in t["numeric_ranges"].items()
                                   if k in ("AMOUNT", "QTY", "MARK", "revenue", "qty", "gross_profit", "qty_onhand")}
                    if interesting:
                        lines.append("- Số liệu (min–max trong mẫu):")
                        for col, nr in interesting.items():
                            lines.append(f"  - `{col}`: {nr['min']} – {nr['max']}")

                if t.get("tcvn3_examples"):
                    lines.append("- Ví dụ TCVN3 → Unicode:")
                    for ex in t["tcvn3_examples"]:
                        lines.append(f"  - `{ex['column']}`: `{ex['raw']}` → **{ex['decoded']}**")
                lines.append("")

    lines += [
        "## Đúc kết kiến trúc",
        "",
        "### db1 — archive giao dịch (shard)",
        "",
        "| Logical | Physical | Ghi chú |",
        "|---------|----------|---------|",
        "| STRANS | `STRANS_YYYYMM` (29 bảng) | Chi tiết dòng bán, 114 cột |",
        "| PMTRANS | `PMTRANS_YYYYMM` (28 bảng) | Thanh toán, 27 cột |",
        "| CRDTRANS | `CRDTRANS_ARC` | Giao dịch thẻ/điểm |",
        "| TRANSHDR | `TRANSHDR_ARC` | Header bill |",
        "",
        "Chọn shard theo `TRAN_DATE` → `STRANS_202503` cho tháng 03/2025.",
        "",
        "### db2 — vận hành + master + báo cáo",
        "",
        "- **Live transactions:** `TRANSHDR`, `STRANS`, `PMTRANS`, `CRDTRANS` (không shard; window gần đây)",
        "- **Staging:** `SUSPEND`, `*_TMP` — bill treo / chưa post",
        "- **Master:** `CUSTOMER`, `CSCARD`, `SKU_DEF`, `SUPPLIER`, …",
        "- **Pre-aggregated:** `WebRpt_*` — ưu tiên cho agent analytics",
        "",
        "## Mã nghiệp vụ quan sát được (cần xác nhận)",
        "",
        "| Mã | Bảng thường gặp | Dự đoán |",
        "|----|-----------------|---------|",
        "| `221` | PMTRANS | Thanh toán bán lẻ |",
        "| `008` | PMTRANS | Thu/chi quỹ (số tiền lớn) |",
        "| `113` | STRANS, TRANSHDR | Bán lẻ — chi tiết/header |",
        "| `811`/`812` | CRDTRANS | Tích/điều chỉnh điểm thẻ |",
        "| `222`, `320`, `010`, `340` | PMTRANS/STRANS | Loại chứng từ khác |",
        "",
        "**PMT_CODE:** `CASH`, `CARD`, `BANK`, `OWNCP` (thường có trailing space).",
        "",
        "**Điểm thưởng:** `AMOUNT / MARK ≈ 50,000` trên mẫu CRDTRANS (khớp rule điểm/50k trong domain_definitions stub).",
        "",
        "**Thẻ:** prefix `A`, `E`, `F`, `H` — có thể map tier/loại thẻ (cần bạn xác nhận).",
        "",
        "## Khuyến nghị cho data_dictionary / agent",
        "",
        "1. Logical table + shard resolver cho db1 (`data_dictionary/db1/shards.yaml`).",
        "2. Mô tả cột ưu tiên bảng `WebRpt_*` và master (`SKU_DEF`, `CSCARD`) trước raw STRANS.",
        "3. `domain_definitions.md`: map `TRANS_CODE`, `PMT_CODE`, prefix `CARD_ID`.",
        "4. Pipeline decode TCVN3 trên mọi string từ SQL trước khi đưa LLM/sandbox.",
        "5. Agent II query `WebRpt_*` khi câu hỏi aggregate; chỉ đục STRANS/PMTRANS shard khi cần chi tiết.",
        "",
        "---",
        f"*Generated by `scripts/explore_db_deep.py` — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
    ]
    return "\n".join(lines)


def explore_db(label: str, dsn_env: str, schema_map: dict[str, dict]) -> dict[str, Any]:
    tables = list(schema_map.keys())
    print(f"\n=== {label} ({len(tables)} tables) ===")
    conn = connect(dsn_env)
    analyzed: list[dict[str, Any]] = []
    errors = 0
    try:
        for i, table in enumerate(tables, 1):
            sample = sample_table(conn, table)
            result = analyze_table(table, schema_map[table], sample)
            analyzed.append(result)
            mark = "OK" if result.get("status") == "ok" else "ERR"
            print(f"  [{i}/{len(tables)}] {table}: {mark}")
            if result.get("status") == "error":
                errors += 1
    finally:
        conn.close()
    return {
        "label": label,
        "table_count": len(tables),
        "errors": errors,
        "tables": analyzed,
        "global": global_aggregates(analyzed),
    }


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    db1_schema = load_schema(ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B3.json")
    db2_schema = load_schema(ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B5.json")

    db1 = explore_db("db1_RESTORED_DB", "ANALYTICS_DB_DSN", db1_schema)
    db2 = explore_db("db2_RESTORED_DB2", "ANALYTICS_DB_DSN_2", db2_schema)

    payload = {
        "max_rows_per_table": MAX_ROWS,
        "db1": db1,
        "db2": db2,
    }

    OUT_SAMPLES.mkdir(parents=True, exist_ok=True)
    raw_path = OUT_SAMPLES / "deep_analysis.json"

    # Strip decoded_rows from JSON dump (large) — keep in memory for report only
    slim = json.loads(json.dumps(payload, default=_json_default))
    for db_key in ("db1", "db2"):
        for t in slim[db_key]["tables"]:
            t.pop("decoded_rows", None)
    raw_path.write_text(json.dumps(slim, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")

    report = render_report(payload)
    RAW_REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nWrote {raw_path}")
    print(f"Wrote {RAW_REPORT_PATH}")
    print("(Semantic report: docs/DB_EXPLORATION_REPORT.md — maintain separately)")


if __name__ == "__main__":
    main()
