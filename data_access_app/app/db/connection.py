"""ODBC connections for db1 / db2."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import pandas as pd
import pyodbc

from app.config import settings


class DbError(RuntimeError):
    pass


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
    except Exception as exc:  # noqa: BLE001
        raise DbError(f"Không kết nối được SQL Server: {exc}") from exc


@contextmanager
def connection(target: str) -> Iterator[pyodbc.Connection]:
    target = target.lower().strip()
    dsn = settings.dsn_db1 if target == "db1" else settings.dsn_db2
    if target not in {"db1", "db2"}:
        raise DbError(f"target_db không hợp lệ: {target}")
    conn = _connect(dsn)
    try:
        yield conn
    finally:
        conn.close()


def test_connection(target: str) -> str:
    with connection(target) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 AS ok")
        row = cur.fetchone()
        return f"{target}: OK (SELECT 1 = {row[0] if row else '?'})"


def read_sql(target: str, sql: str, params: list[Any] | tuple[Any, ...] | None = None) -> pd.DataFrame:
    with connection(target) as conn:
        return pd.read_sql(sql, conn, params=params or [])
