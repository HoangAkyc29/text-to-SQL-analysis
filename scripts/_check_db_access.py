#!/usr/bin/env python3
"""Quick check: dictionary exploration ODBC (NOT agent ANALYTICS_DB_DSN)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from dictionary_exploration_db import (  # noqa: E402
    connection_info,
    load_exploration_env,
    resolve_dsn,
)

load_exploration_env()


def main() -> None:
    import pyodbc

    cfg_server = connection_info("db1").get("server", "?")
    uid_dsn = resolve_dsn("db1")
    # probe via master (login without initial catalog)
    import re

    m = re.search(r"Uid=([^;]+)", uid_dsn)
    p = re.search(r"Pwd=([^;]+)", uid_dsn)
    srv = re.search(r"Server=([^;]+)", uid_dsn)
    if not (m and p and srv):
        print("Cannot parse DSN for diagnostic")
        return
    master_dsn = (
        f"Driver={{ODBC Driver 18 for SQL Server}};Server={srv.group(1)};"
        f"Database=master;Uid={m.group(1)};Pwd={p.group(1)};TrustServerCertificate=yes;"
    )
    try:
        conn = pyodbc.connect(master_dsn, timeout=15)
        cur = conn.cursor()
        cur.execute("SELECT @@SERVERNAME, SUSER_SNAME()")
        row = cur.fetchone()
        print(f"master: OK  server={row[0]}  login={row[1]}  target_host={srv.group(1)}")
        for db in ("RESTORED_DB", "RESTORED_DB2"):
            cur.execute("SELECT HAS_DBACCESS(?)", db)
            access = cur.fetchone()[0]
            status = "OK" if access else "NO ACCESS"
            print(f"  HAS_DBACCESS({db}) = {access}  ({status})")
        conn.close()
    except Exception as exc:
        print(f"master: FAIL  {exc}")
        return

    for ds in ("db1", "db2"):
        info = connection_info(ds)
        try:
            conn = pyodbc.connect(resolve_dsn(ds), timeout=15)
            cur = conn.cursor()
            cur.execute("SELECT DB_NAME(), USER_NAME()")
            row = cur.fetchone()
            print(f"{ds}: OK  {info}  db={row[0]}  user={row[1]}")
            conn.close()
        except Exception as exc:
            print(f"{ds}: FAIL  {info}")
            print(f"       {exc}")


if __name__ == "__main__":
    main()
