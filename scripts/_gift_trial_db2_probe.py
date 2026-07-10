import os, sys
from pathlib import Path
import pyodbc

ROOT = Path("/app")
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
from project_core.config.env import load_project_env

load_project_env(ROOT)
dsn = os.environ.get("ANALYTICS_DB_DSN_2")
if not dsn:
    print("ERROR: ANALYTICS_DB_DSN_2 not set")
    sys.exit(1)

queries = [
    ("Q1 SKU_DEF",
     "SELECT TOP 5 SKU_ID, SKU_CODE FROM SKU_DEF "
     "WHERE SKU_CODE IN ('0030344','0030348','0030355') "
     "OR SKU_CODE IN ('00030344','00030348','00030355')"),
    ("Q2 BARCODE",
     "SELECT TOP 5 BARCODE, SKU_ID FROM BARCODE "
     "WHERE BARCODE IN ('0030344','0030348','0030355')"),
    ("Q3 TRANSHDR count",
     "SELECT COUNT(*) AS cnt FROM TRANSHDR "
     "WHERE TRAN_DATE >= '2026-07-01' AND TRAN_DATE <= '2026-07-06' "
     "AND TRANS_CODE='113' AND AMOUNT >= 600000"),
]

c = pyodbc.connect(dsn, timeout=30)
cur = c.cursor()
for label, sql in queries:
    print("=" * 60)
    print(label)
    print(sql)
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        print(f"row_count: {len(rows)}")
        if cols:
            print("columns:", cols)
        for r in rows:
            print(tuple(r))
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
c.close()
print("done")
