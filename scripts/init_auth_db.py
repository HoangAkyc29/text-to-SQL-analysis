#!/usr/bin/env python3
"""Initialize AUTH DB contents: schema + capability RBAC + seed users.

Assumes the database `supermarket_auth` ALREADY EXISTS and that `AUTH_DB_DSN`
points at it with a SQL login that has enough rights (create tables + write —
e.g. db_owner on that DB). This script does NOT touch `master` and does NOT run
`CREATE DATABASE`.

    uv run python scripts/init_auth_db.py

Server is taken from AUTH_DB_DSN; when running on the host the container-only
host `host.docker.internal` is rewritten to `localhost` (override with
`AUTH_DB_INIT_SERVER`, e.g. `localhost,14330`).

Steps: 001_schema -> 003_password_login -> 004_permissions -> seed_auth.py.
Idempotent and safe to re-run.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from project_core.config.env import load_project_env  # noqa: E402

AUTH_DIR = ROOT / "deploy" / "sql" / "auth"


def parse_dsn(dsn: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in dsn.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().lower()] = v.strip()
    return out


def run_file(cursor, path: Path) -> None:
    cursor.execute(path.read_text(encoding="utf-8"))
    print(f"[ok] ran {path.name}")


def main() -> None:
    load_project_env()
    dsn = os.getenv("AUTH_DB_DSN", "").strip()
    if not dsn:
        raise SystemExit("AUTH_DB_DSN not set (see .env)")
    p = parse_dsn(dsn)

    driver = p.get("driver", "ODBC Driver 18 for SQL Server").strip("{}")
    server = os.getenv("AUTH_DB_INIT_SERVER") or p["server"].replace(
        "host.docker.internal", "localhost"
    )
    database = p.get("database", "supermarket_auth")
    uid = p.get("uid", "")
    pwd = p.get("pwd", "")

    db_cs = (
        f"Driver={{{driver}}};Server={server};Database={database};"
        f"Uid={uid};Pwd={pwd};TrustServerCertificate=yes;"
    )
    print(f"[info] connecting to {server}/{database} as {uid}")

    try:
        conn = pyodbc.connect(db_cs, autocommit=True, timeout=10)
    except pyodbc.Error as exc:
        msg = str(exc)
        if "18456" in msg:
            raise SystemExit(
                f"Login failed for '{uid}'. Check Uid/Pwd in AUTH_DB_DSN."
            ) from exc
        if "4060" in msg or "Cannot open database" in msg:
            raise SystemExit(
                f"Database '{database}' not found or no access. Create it first "
                f"and grant the login rights on it."
            ) from exc
        raise

    with conn:
        cur = conn.cursor()
        cur.execute("SELECT OBJECT_ID('users')")
        if cur.fetchone()[0] is None:
            run_file(cur, AUTH_DIR / "001_schema.sql")
        else:
            print("[skip] users table exists — skip 001_schema.sql")
        run_file(cur, AUTH_DIR / "003_password_login.sql")
        run_file(cur, AUTH_DIR / "004_permissions.sql")

    # Seed users with runtime-hashed passwords, reusing this connection string.
    os.environ["AUTH_DB_DSN"] = db_cs
    import seed_auth

    seed_auth.main()

    with pyodbc.connect(db_cs, timeout=10) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username, role FROM users ORDER BY username")
        print("[verify] users:", [tuple(r) for r in cur.fetchall()])
        cur.execute("SELECT role_key, COUNT(*) FROM role_permissions GROUP BY role_key")
        print("[verify] role_permissions:", [tuple(r) for r in cur.fetchall()])
    print("[done] AUTH DB schema + RBAC + users ready.")


if __name__ == "__main__":
    main()
