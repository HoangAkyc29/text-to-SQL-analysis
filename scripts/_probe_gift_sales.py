#!/usr/bin/env python3
import os, sys
from pathlib import Path
import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
from project_core.config.env import load_project_env

load_project_env(ROOT)
dsn = os.environ.get("ANALYTICS_DB_DSN_2")
c = pyodbc.connect(dsn, timeout=15)
cur = c.cursor()
sql = """
WITH gift_sku AS (
  SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355')
),
valid_bills AS (
  SELECT TRANS_NUM FROM TRANSHDR
  WHERE TRANS_CODE = '113' AND TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07' AND AMOUNT >= 600000
)
SELECT s.SKU_ID, SUM(s.QTY) q, COUNT(DISTINCT s.TRANS_NUM) bills
FROM STRANS s
INNER JOIN gift_sku g ON g.SKU_ID = s.SKU_ID
INNER JOIN valid_bills v ON v.TRANS_NUM = s.TRANS_NUM
WHERE s.TRANS_CODE='113' AND s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
GROUP BY s.SKU_ID
"""
cur.execute(sql)
print("Gift qty valid bills:", cur.fetchall())
cur.execute("SELECT COUNT(*) FROM STRANS WHERE TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'")
print("STRANS rows july:", cur.fetchone()[0])
c.close()
