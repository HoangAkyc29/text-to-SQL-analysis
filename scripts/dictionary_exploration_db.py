"""ODBC connectivity for dictionary/column exploration scripts only — not used by agents."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "dictionary_exploration.yaml"


class DictionaryExplorationConfigError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load_yaml() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise DictionaryExplorationConfigError(f"Missing config: {CONFIG_PATH}")
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_exploration_env(root: Path | None = None) -> Path:
    """Load ONLY .env.dictionary_exploration — never agent .env."""
    root = root or ROOT
    cfg = _load_yaml()
    env_name = str(cfg.get("env_file") or ".env.dictionary_exploration")
    env_path = root / env_name
    if env_path.exists():
        load_dotenv(env_path, override=True)
    return env_path


def _build_dsn(server: str, database: str, uid: str, pwd: str) -> str:
    cfg = _load_yaml()
    conn = cfg.get("connection") or {}
    driver = str(conn.get("driver") or "ODBC Driver 18 for SQL Server")
    trust = conn.get("trust_server_certificate", True)
    trust_part = "TrustServerCertificate=yes;" if trust else ""
    return (
        f"Driver={{{driver}}};Server={server};Database={database};"
        f"Uid={uid};Pwd={pwd};{trust_part}"
    )


def resolve_dsn(data_source: str) -> str:
    """Return ODBC connection string for db1 or db2."""
    if data_source not in {"db1", "db2"}:
        raise ValueError(f"data_source must be db1|db2, got {data_source!r}")

    load_exploration_env()
    cfg = _load_yaml()
    db_cfg = (cfg.get("databases") or {}).get(data_source) or {}
    dsn_env = str(db_cfg.get("dsn_env") or f"DICTIONARY_EXPLORE_{data_source.upper()}_DSN")
    explicit = os.getenv(dsn_env, "").strip()
    if explicit:
        return explicit

    cred = cfg.get("credential_env") or {}
    uid = os.getenv(str(cred.get("uid") or "DICTIONARY_EXPLORE_UID"), "").strip()
    pwd = os.getenv(str(cred.get("pwd") or "DICTIONARY_EXPLORE_PWD"), "").strip()
    local = cfg.get("local") or {}
    server = str(local.get("server") or "DESKTOP-AUQEDC5")
    database = str(db_cfg.get("database") or ("RESTORED_DB" if data_source == "db1" else "RESTORED_DB2"))

    if not uid or not pwd or pwd == "CHANGE_ME":
        example = ROOT / ".env.dictionary_exploration.example"
        raise DictionaryExplorationConfigError(
            f"{data_source}: set {dsn_env} or {cred.get('uid', 'DICTIONARY_EXPLORE_UID')}/"
            f"{cred.get('pwd', 'DICTIONARY_EXPLORE_PWD')} in .env.dictionary_exploration "
            f"(copy from {example.name}). Explore scripts do not use ANALYTICS_DB_DSN."
        )
    return _build_dsn(server, database, uid, pwd)


def connection_info(data_source: str) -> dict[str, str]:
    """Safe metadata for logs (no secrets)."""
    cfg = _load_yaml()
    db_cfg = (cfg.get("databases") or {}).get(data_source) or {}
    local = cfg.get("local") or {}
    dsn_env = str(db_cfg.get("dsn_env") or f"DICTIONARY_EXPLORE_{data_source.upper()}_DSN")
    if os.getenv(dsn_env, "").strip():
        return {"data_source": data_source, "mode": "dsn_env", "env_var": dsn_env}
    return {
        "data_source": data_source,
        "mode": "built",
        "server": str(local.get("server") or "DESKTOP-AUQEDC5"),
        "database": str(db_cfg.get("database") or ""),
    }


def connect(data_source: str, *, timeout: int = 120):
    import pyodbc

    dsn = resolve_dsn(data_source)
    try:
        return pyodbc.connect(dsn, timeout=timeout)
    except pyodbc.Error as exc:
        if _is_database_access_denied(exc, data_source):
            raise DictionaryExplorationConfigError(
                _database_access_help(data_source, exc)
            ) from exc
        raise


def _is_database_access_denied(exc: Exception, data_source: str) -> bool:
    text = str(exc).lower()
    cfg = _load_yaml()
    db = ((cfg.get("databases") or {}).get(data_source) or {}).get("database", "")
    return "4060" in text or (db.lower() in text and "login failed" in text)


def _database_access_help(data_source: str, exc: Exception) -> str:
    cfg = _load_yaml()
    db = str(((cfg.get("databases") or {}).get(data_source) or {}).get("database") or data_source)
    local = cfg.get("local") or {}
    server = str(local.get("server") or "DESKTOP-AUQEDC5,14330")
    return (
        f"Login OK nhưng user không có quyền mở database `{db}` (HAS_DBACCESS=0). "
        f"Password/host đúng — đây là lỗi SQL permission, không phải sai mật khẩu. "
        f"Docker dùng cùng SQL `{server}` → cùng user sẽ gặp lỗi tương tự nếu chưa GRANT. "
        f"Cần DBA: map login vào DB + db_datareader trên `{db}`. "
        f"Chi tiết: {exc}"
    )
