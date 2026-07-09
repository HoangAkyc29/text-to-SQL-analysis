#!/usr/bin/env python3
import os, sys
from pathlib import Path
import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
from project_core.config.env import load_project_env

load_project_env(ROOT)
dsn = os.environ.get("ANALYTICS_DB_DSN_2") or os.environ.get("ANALYTICS_DB_DSN")
c = pyodbc.connect(dsn, timeout=15)
cur = c.cursor()
cur.execute(
    "SELECT TOP 20 SKU_ID, SKU_CODE, BARCODE FROM SKU_DEF "
    "WHERE SKU_CODE LIKE '%30344%' OR SKU_CODE LIKE '%30348%' OR SKU_CODE LIKE '%30355%'"
)
print("SKU_DEF matches:", cur.fetchall())
cur.execute(
    "SELECT TOP 10 s.SKU_ID, SUM(s.QTY) q FROM STRANS s "
    "WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07' AND s.TRANS_CODE='113' "
    "GROUP BY s.SKU_ID ORDER BY SUM(s.QTY) DESC"
)
print("Top SKUs July:", cur.fetchall())
c.close()
