"""Load project environment — root .env only."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def project_root(root_dir: Path | None = None) -> Path:
    if root_dir is not None:
        return root_dir
    env_root = os.getenv("AGENT_ROOT_DIR")
    if env_root:
        return Path(env_root)
    return Path.cwd()


def load_project_env(root_dir: Path | None = None) -> Path:
    """Load ``<project_root>/.env``. Returns path to .env (may not exist)."""
    root = project_root(root_dir)
    path = root / ".env"
    load_dotenv(path)
    return path
