#!/usr/bin/env python3
"""Remove artifact traces older than configured TTL."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.loader import load_project_config  # noqa: E402


def cleanup(*, dry_run: bool = False) -> int:
    cfg = load_project_config()
    base = Path(cfg.artifacts.base_dir)
    if not base.exists():
        print(f"No artifacts dir: {base}")
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=cfg.artifacts.ttl_days)
    removed = 0
    for child in base.iterdir():
        if not child.is_dir():
            continue
        mtime = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            removed += 1
            print(f"{'would remove' if dry_run else 'removing'} {child}")
            if not dry_run:
                shutil.rmtree(child, ignore_errors=True)
    print(f"done: {removed} trace(s)")
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup stale analysis artifacts")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cleanup(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
