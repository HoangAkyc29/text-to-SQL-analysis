from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import bcrypt
import pyodbc

from project_core.domain.access.permission_set import PermissionSet
from project_core.domain.access.user_claims import normalize_store_ids

logger = logging.getLogger(__name__)

_perm_cache: dict[str, tuple[float, PermissionSet]] = {}
_PERM_CACHE_TTL = float(os.getenv("AUTH_PERMISSIONS_CACHE_TTL", "60"))


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    username: str
    role: str
    store_ids: list[int] | None
    display_name: str
    email: str


def _connect() -> pyodbc.Connection:
    dsn = os.getenv("AUTH_DB_DSN", "").strip()
    if not dsn:
        raise RuntimeError("AUTH_DB_DSN not configured")
    return pyodbc.connect(dsn, timeout=15)


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _row_to_user(row: Any) -> AuthUser:
    store_raw = row.store_ids if hasattr(row, "store_ids") else row[4]
    return AuthUser(
        user_id=str(row.user_id if hasattr(row, "user_id") else row[0]),
        username=str(row.username if hasattr(row, "username") else row[1]),
        role=str(row.role if hasattr(row, "role") else row[2]),
        store_ids=normalize_store_ids(store_raw),
        display_name=str(row.display_name if hasattr(row, "display_name") else row[5]),
        email=str(row.email if hasattr(row, "email") else row[6]),
    )


def authenticate(username: str, password: str) -> AuthUser | None:
    """Lookup user by username and verify bcrypt password_hash."""
    username = username.strip()
    if not username or not password:
        return None
    try:
        with _connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, username, role, password_hash, store_ids, display_name, email
                FROM users
                WHERE username = ? AND is_active = 1
                """,
                username,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            password_hash = str(row.password_hash if hasattr(row, "password_hash") else row[3])
            if not verify_password(password, password_hash):
                return None
            return _row_to_user(row)
    except pyodbc.Error as exc:
        logger.warning("AUTH_DB login failed: %s", exc)
        return None
    except RuntimeError:
        logger.warning("AUTH_DB_DSN missing — cannot authenticate")
        return None


def load_effective_permissions(user_id: str) -> PermissionSet | None:
    """Resolve capability keys for a user from the AUTH DB.

    Effective = role_permissions[user.role] UNION user_permissions(grant)
                MINUS user_permissions(revoke).

    Returns ``None`` when the user is inactive/absent or the DB / permission
    tables are unavailable. Callers treat ``None`` as fail-closed (deny access);
    only dev mode (``ALLOW_DEV_AUTH=1``) falls back to YAML roles. Cached per
    user with a short TTL to avoid a DB round-trip on every ``/chat``.
    """
    now = time.monotonic()
    cached = _perm_cache.get(user_id)
    if cached and cached[0] > now:
        return cached[1]
    try:
        with _connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role FROM users WHERE user_id = ? AND is_active = 1",
                user_id,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            role = str(row[0])
            cursor.execute(
                "SELECT permission_key FROM role_permissions WHERE role_key = ?",
                role,
            )
            keys = {str(r[0]) for r in cursor.fetchall()}
            cursor.execute(
                "SELECT permission_key, effect FROM user_permissions WHERE user_id = ?",
                user_id,
            )
            for pk, effect in cursor.fetchall():
                if str(effect).lower() == "revoke":
                    keys.discard(str(pk))
                else:
                    keys.add(str(pk))
            perm_set = PermissionSet.from_keys(keys)
            _perm_cache[user_id] = (now + _PERM_CACHE_TTL, perm_set)
            return perm_set
    except pyodbc.Error as exc:
        logger.warning("AUTH_DB permissions load failed: %s", exc)
        return None
    except RuntimeError:
        logger.warning("AUTH_DB_DSN missing — cannot load permissions")
        return None


def get_user_by_id(user_id: str) -> AuthUser | None:
    try:
        with _connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, username, role, password_hash, store_ids, display_name, email
                FROM users
                WHERE user_id = ? AND is_active = 1
                """,
                user_id,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return _row_to_user(row)
    except Exception as exc:  # noqa: BLE001
        logger.warning("AUTH_DB lookup failed: %s", exc)
        return None
