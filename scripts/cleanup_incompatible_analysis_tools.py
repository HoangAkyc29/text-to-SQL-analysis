#!/usr/bin/env python3
"""Dry-run/apply cleanup limited to incompatible analysis_tools records."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402
from project_core.domain.feedback.analysis_tool_cleanup import (  # noqa: E402
    cleanup_incompatible_analysis_tools,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Delete matched analysis_tools records (default is dry-run).",
    )
    args = parser.parse_args()
    load_project_env(ROOT)

    from pymongo import MongoClient

    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    result = cleanup_incompatible_analysis_tools(
        db["analysis_tools"], apply=args.apply
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
