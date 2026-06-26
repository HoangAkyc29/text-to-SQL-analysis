"""Runtime data paths (shared by project-core, MCP servers, and agents)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.getenv("AGENT_ROOT_DIR", Path.cwd()))
DATA_DIR = Path(os.getenv("AGENT_DATA_DIR", ROOT / "data"))
STATE_DB = DATA_DIR / "state" / "project_state.db"
CHECKPOINTS = DATA_DIR / "checkpoints.db"
AUDIT_LOG = DATA_DIR / "state" / "audit.jsonl"

(DATA_DIR / "stm").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "state").mkdir(parents=True, exist_ok=True)
