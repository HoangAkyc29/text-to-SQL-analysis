"""Quick ODBC smoke test for data_access_app."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.db.connection import DbError, test_connection


def main() -> int:
    settings.reload()
    for name, dsn in (("db1", settings.dsn_db1), ("db2", settings.dsn_db2)):
        server = re.search(r"Server=([^;]+)", dsn or "", re.I)
        database = re.search(r"Database=([^;]+)", dsn or "", re.I)
        print(
            f"{name}: Server={server.group(1) if server else '?'} "
            f"Database={database.group(1) if database else '?'}"
        )
    ok = True
    for target in ("db2", "db1"):
        try:
            print(test_connection(target))
        except DbError as exc:
            ok = False
            print(f"{target} FAIL: {exc}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"{target} ERROR: {type(exc).__name__}: {exc}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
