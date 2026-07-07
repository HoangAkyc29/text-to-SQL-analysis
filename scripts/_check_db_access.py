#!/usr/bin/env python3
"""Quick check: db1/db2 ODBC access from env."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
from project_core.config.env import load_project_env  # noqa: E402

load_project_env(ROOT)

for key in ("ANALYTICS_DB_DSN", "ANALYTICS_DB_DSN_2"):
    dsn = os.getenv(key, "")
    db_name = "?"
    if "Database=" in dsn:
        db_name = dsn.split("Database=")[1].split(";", 1)[0]
    try:
        conn = pyodbc.connect(dsn, timeout=15)
        cur = conn.cursor()
        cur.execute("SELECT DB_NAME(), USER_NAME()")
        row = cur.fetchone()
        print(f"{key}: OK  connected_db={row[0]}  user={row[1]}  dsn_db={db_name}")
        conn.close()
    except Exception as exc:
        print(f"{key}: FAIL  dsn_db={db_name}  error={exc}")

# From db1 connection, check HAS_DBACCESS
dsn1 = os.getenv("ANALYTICS_DB_DSN", "")
if dsn1:
    conn = pyodbc.connect(dsn1, timeout=15)
    cur = conn.cursor()
    for db in ("RESTORED_DB", "RESTORED_DB2"):
        cur.execute(f"SELECT HAS_DBACCESS('{db}')")
        ok = cur.fetchone()[0]
        print(f"HAS_DBACCESS({db}) = {ok}")
    conn.close()
