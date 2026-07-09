#!/usr/bin/env python3
"""Generate data_dictionary/columns/*.md — delegates to sample-aware enrichment."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    # Ensure inventory exists
    build = ROOT / "scripts" / "build_column_semantics.py"
    subprocess.run([sys.executable, str(build)], check=True, cwd=ROOT)
    enrich = ROOT / "scripts" / "enrich_column_docs_from_samples.py"
    return subprocess.run([sys.executable, str(enrich)], cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
