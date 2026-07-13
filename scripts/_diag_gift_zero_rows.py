"""Diagnose why agent gift main query returned 0 rows."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
from project_core.config.env import load_project_env  # noqa: E402

load_project_env(ROOT)
dsn = os.environ.get("ANALYTICS_DB_DSN_2")
if not dsn:
    raise SystemExit("ANALYTICS_DB_DSN_2 missing")

c = pyodbc.connect(dsn, timeout=60)
cur = c.cursor()


def run(label: str, sql: str) -> None:
    print("=" * 70)
    print(label)
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        print(f"rows={len(rows)}")
        for r in rows[:20]:
            print(tuple(r))
    except Exception as e:  # noqa: BLE001
        print("ERROR", e)


run(
    "SKU resolve",
    """
SELECT SKU_ID, SKU_CODE, FULL_NAME FROM SKU_DEF
WHERE SKU_CODE IN ('00030344','00030348','00030355')
""",
)

run(
    "STRANS any for SKUs in date (no TRANS_CODE)",
    """
SELECT COUNT(*) cnt, COUNT(DISTINCT TRANS_NUM) bills, COUNT(DISTINCT SKU_ID) skus
FROM STRANS
WHERE TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'
  AND SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
""",
)

run(
    "STRANS same + TRANS_CODE=113",
    """
SELECT COUNT(*) cnt, COUNT(DISTINCT TRANS_NUM) bills
FROM STRANS
WHERE TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'
  AND TRANS_CODE='113'
  AND SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
""",
)

run(
    "Agent-style: gift ∩ ValidBills TRANSHDR.AMOUNT>=600k + TRANS_CODE=113 both",
    """
WITH pr AS (
  SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355')
), vb AS (
  SELECT TRANS_NUM FROM TRANSHDR
  WHERE TRANS_CODE='113' AND TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'
    AND AMOUNT >= 600000
)
SELECT COUNT(*) cnt FROM STRANS s
JOIN pr ON s.SKU_ID = pr.SKU_ID
JOIN vb ON s.TRANS_NUM = vb.TRANS_NUM
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
  AND s.TRANS_CODE='113'
""",
)

run(
    "Gift ∩ ValidBills, drop STRANS.TRANS_CODE filter",
    """
WITH pr AS (
  SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355')
), vb AS (
  SELECT TRANS_NUM FROM TRANSHDR
  WHERE TRANS_CODE='113' AND TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'
    AND AMOUNT >= 600000
)
SELECT COUNT(*) cnt FROM STRANS s
JOIN pr ON s.SKU_ID = pr.SKU_ID
JOIN vb ON s.TRANS_NUM = vb.TRANS_NUM
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
""",
)

run(
    "Gift lines join any TRANSHDR same TRANS_NUM (no amount)",
    """
WITH pr AS (
  SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355')
)
SELECT COUNT(*) cnt, COUNT(DISTINCT s.TRANS_NUM) bills
FROM STRANS s
JOIN pr ON s.SKU_ID = pr.SKU_ID
JOIN TRANSHDR h ON s.TRANS_NUM = h.TRANS_NUM
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
""",
)

run(
    "Sample STRANS gift lines",
    """
SELECT TOP 15 s.SKU_ID, s.TRANS_NUM, s.TRAN_DATE, s.TRANS_CODE, s.STK_ID, s.QTY, s.AMOUNT
FROM STRANS s
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
  AND s.SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
""",
)

run(
    "Ground-truth style: gift on bills with SUM(AMT+SURPLUS+VAT)>=600k",
    """
WITH pr AS (
  SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355')
), bill AS (
  SELECT STK_ID, TRANS_NUM,
         SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) AS BILL_VALUE
  FROM STRANS
  WHERE TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'
  GROUP BY STK_ID, TRANS_NUM
)
SELECT COUNT(*) gift_lines, COUNT(DISTINCT s.TRANS_NUM) bills
FROM STRANS s
JOIN pr ON s.SKU_ID = pr.SKU_ID
JOIN bill b ON b.STK_ID = s.STK_ID AND b.TRANS_NUM = s.TRANS_NUM AND b.BILL_VALUE >= 600000
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
""",
)

run(
    "Gift lines any bill sum (no 600k), all stores",
    """
WITH pr AS (
  SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355')
)
SELECT COUNT(*) gift_lines, COUNT(DISTINCT TRANS_NUM) bills, COUNT(DISTINCT STK_ID) stores
FROM STRANS s
JOIN pr ON s.SKU_ID = pr.SKU_ID
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
""",
)

c.close()
print("done")
