#!/usr/bin/env python3
"""Seed AUTH DB users. Passwords are hashed + salted at runtime (bcrypt).

Security rules enforced here:
  * No password hash is ever committed to source control.
  * Each user has its OWN password (never a shared secret).
  * Each password gets its own random bcrypt salt (rounds=12).
  * Real passwords are supplied via per-user env vars; the built-in defaults
    are bootstrap-only and must be rotated before production.

Usage (recommended — set per-user env vars, e.g. in .env):
    AUTH_SEED_ADMIN_PASSWORD=...        \\
    AUTH_SEED_HQ_ANALYST_PASSWORD=...   \\
    AUTH_SEED_STORE_MANAGER_PASSWORD=...  uv run python scripts/seed_auth.py

Idempotent: re-running upserts the same three users (stable user_id GUIDs) and
does not touch other rows.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import bcrypt
import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402


@dataclass(frozen=True)
class SeedUser:
    user_id: str
    username: str
    email: str
    display_name: str
    role: str
    store_ids: str | None
    password_env: str
    default_password: str


SEED_USERS = [
    SeedUser(
        user_id="11111111-1111-1111-1111-111111111111",
        username="store.manager",
        email="manager@store.local",
        display_name="Store Manager",
        role="store_manager",
        store_ids="10001,10004",
        password_env="AUTH_SEED_STORE_MANAGER_PASSWORD",
        default_password="St0reManager!Seed#26",
    ),
    SeedUser(
        user_id="22222222-2222-2222-2222-222222222222",
        username="hq.analyst",
        email="analyst@hq.local",
        display_name="HQ Analyst",
        role="hq_analyst",
        store_ids=None,
        password_env="AUTH_SEED_HQ_ANALYST_PASSWORD",
        default_password="HqAn@lyst!Seed#26",
    ),
    SeedUser(
        user_id="33333333-3333-3333-3333-333333333333",
        username="admin",
        email="admin@hq.local",
        display_name="Administrator",
        role="admin",
        store_ids=None,
        password_env="AUTH_SEED_ADMIN_PASSWORD",
        default_password="Adm1n@Superm@rket#26",
    ),
]

UPSERT_SQL = """
MERGE users AS tgt
USING (SELECT ? AS user_id, ? AS username, ? AS email, ? AS display_name,
              ? AS role, ? AS store_ids, ? AS password_hash) AS src
ON tgt.username = src.username
WHEN MATCHED THEN UPDATE SET
    email = src.email,
    display_name = src.display_name,
    role = src.role,
    store_ids = src.store_ids,
    password_hash = src.password_hash,
    is_active = 1
WHEN NOT MATCHED THEN INSERT
    (user_id, username, email, display_name, role, store_ids, password_hash, is_active)
    VALUES (src.user_id, src.username, src.email, src.display_name,
            src.role, src.store_ids, src.password_hash, 1);
"""


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _resolve_password(user: SeedUser) -> tuple[str, bool]:
    """Return (password, is_default). Env var wins over the bootstrap default."""
    env_val = os.getenv(user.password_env, "").strip()
    if env_val:
        return env_val, False
    return user.default_password, True


def main() -> None:
    load_project_env()
    dsn = os.getenv("AUTH_DB_DSN", "").strip()
    if not dsn:
        raise SystemExit("AUTH_DB_DSN not set (see .env)")

    used_defaults: list[str] = []
    with pyodbc.connect(dsn, timeout=15) as conn:
        cursor = conn.cursor()
        for user in SEED_USERS:
            password, is_default = _resolve_password(user)
            if is_default:
                used_defaults.append(user.username)
            cursor.execute(
                UPSERT_SQL,
                user.user_id,
                user.username,
                user.email,
                user.display_name,
                user.role,
                user.store_ids,
                _hash(password),
            )
            print(f"[ok] upserted {user.username} ({user.role})")
        conn.commit()

    print(f"Seeded {len(SEED_USERS)} users into AUTH DB.")
    if used_defaults:
        print(
            "[warn] bootstrap default password used for: "
            + ", ".join(used_defaults)
            + " — set per-user env vars ("
            + ", ".join(u.password_env for u in SEED_USERS)
            + ") and re-run, or rotate before production."
        )


if __name__ == "__main__":
    main()
