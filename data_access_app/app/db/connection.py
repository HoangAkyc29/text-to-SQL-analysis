"""ODBC connections for db1 / db2 — never leak raw crashes to the UI."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import pandas as pd
import pyodbc

from app.config import settings
from app.db.errors import DbError, is_missing_object_error, wrap_db_exception

# Re-export for existing `from app.db.connection import DbError`
__all__ = ["DbError", "connection", "test_connection", "read_sql"]


def _connect(dsn: str, timeout: int | None = None) -> pyodbc.Connection:
    if not dsn:
        raise DbError("DSN trống — cấu hình ANALYTICS_DB_DSN / ANALYTICS_DB_DSN_2 trong .env")
    t = timeout if timeout is not None else settings.query_timeout
    try:
        # Login timeout via connection string attribute when supported
        attrs = {}
        if hasattr(pyodbc, "SQL_ATTR_CONNECTION_TIMEOUT"):
            attrs[pyodbc.SQL_ATTR_CONNECTION_TIMEOUT] = int(t)
        if hasattr(pyodbc, "SQL_ATTR_LOGIN_TIMEOUT"):
            attrs[pyodbc.SQL_ATTR_LOGIN_TIMEOUT] = min(int(t), 30)
        kwargs: dict = {"timeout": t, "autocommit": True}
        if attrs:
            kwargs["attrs_before"] = attrs
        return pyodbc.connect(dsn, **kwargs)
    except DbError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise wrap_db_exception(exc) from exc


@contextmanager
def connection(target: str) -> Iterator[pyodbc.Connection]:
    target = target.lower().strip()
    dsn = settings.dsn_db1 if target == "db1" else settings.dsn_db2
    if target not in {"db1", "db2"}:
        raise DbError(f"target_db không hợp lệ: {target}")
    try:
        conn = _connect(dsn)
    except DbError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise wrap_db_exception(exc, target=target) from exc
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass


def test_connection(target: str) -> str:
    try:
        with connection(target) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 AS ok")
            row = cur.fetchone()
            return f"{target}: OK (SELECT 1 = {row[0] if row else '?'})"
    except DbError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise wrap_db_exception(exc, target=target) from exc


def read_sql(target: str, sql: str, params: list[Any] | tuple[Any, ...] | None = None) -> pd.DataFrame:
    import time

    from app.db.query_log import log_sql

    t0 = time.perf_counter()
    log_sql(target=target, sql=sql, params=params, phase="start")
    try:
        with connection(target) as conn:
            df = pd.read_sql(sql, conn, params=params or [])
        elapsed = (time.perf_counter() - t0) * 1000
        log_sql(
            target=target,
            sql=sql,
            params=params,
            phase="ok",
            rows=0 if df is None else len(df),
            elapsed_ms=elapsed,
        )
        return df
    except DbError as exc:
        log_sql(
            target=target,
            sql=sql,
            params=params,
            phase="error",
            elapsed_ms=(time.perf_counter() - t0) * 1000,
            error=str(exc),
        )
        raise
    except Exception as exc:  # noqa: BLE001
        log_sql(
            target=target,
            sql=sql,
            params=params,
            phase="error",
            elapsed_ms=(time.perf_counter() - t0) * 1000,
            error=str(exc),
        )
        # Missing shard tables are handled by dual_query; re-raise typed for others.
        if is_missing_object_error(exc):
            raise
        raise wrap_db_exception(exc, target=target) from exc
