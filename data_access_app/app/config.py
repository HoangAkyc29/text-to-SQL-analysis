"""App settings — ODBC DSNs for native host process (not Docker)."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

APP_ROOT = Path(__file__).resolve().parents[1]


def rewrite_docker_host_for_native(dsn: str) -> str:
    """Agent .env uses host.docker.internal for containers → SQL on Windows host.

    This Flet app runs on the host and should use the SQL machine name
    ``DESKTOP-AUQEDC5`` (override with DATA_ACCESS_SQL_SERVER if needed).
    """
    if not dsn:
        return dsn
    override = os.getenv("DATA_ACCESS_SQL_SERVER", "").strip() or "DESKTOP-AUQEDC5"
    if re.search(r"(?i)Server=", dsn):
        return re.sub(r"(?i)Server=[^;]+", f"Server={override}", dsn, count=1)
    return f"Server={override};{dsn}"


@dataclass
class Settings:
    dsn_db1: str = ""
    dsn_db2: str = ""
    output_dir: Path = field(default_factory=lambda: APP_ROOT / "output")
    query_timeout: int = 120
    row_warn: int = 200_000
    # Master-search TOP cap (SKU / CSCARD). Env: DATA_ACCESS_SEARCH_LIMIT
    search_limit: int = 500_000

    def reload(self, env_path: Path | None = None) -> None:
        path = env_path or (APP_ROOT / ".env")
        if path.exists():
            load_dotenv(path, override=True)
        # Fall back to monorepo root .env (Docker-oriented DSNs) then rewrite host.
        root_env = APP_ROOT.parent / ".env"
        if root_env.exists():
            load_dotenv(root_env, override=False)

        raw1 = os.getenv("ANALYTICS_DB_DSN", "").strip()
        raw2 = os.getenv("ANALYTICS_DB_DSN_2", "").strip()
        self.dsn_db1 = rewrite_docker_host_for_native(raw1)
        self.dsn_db2 = rewrite_docker_host_for_native(raw2)
        out = os.getenv("DATA_ACCESS_OUTPUT_DIR", "").strip()
        self.output_dir = Path(out) if out else (APP_ROOT / "output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.query_timeout = int(os.getenv("DATA_ACCESS_QUERY_TIMEOUT", "120") or 120)
        self.row_warn = int(os.getenv("DATA_ACCESS_ROW_WARN", "200000") or 200_000)
        self.search_limit = int(os.getenv("DATA_ACCESS_SEARCH_LIMIT", "500000") or 500_000)

    @property
    def has_db1(self) -> bool:
        return bool(self.dsn_db1)

    @property
    def has_db2(self) -> bool:
        return bool(self.dsn_db2)


settings = Settings()
settings.reload()
