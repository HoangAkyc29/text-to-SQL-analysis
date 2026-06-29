#!/usr/bin/env python3
"""Validate tcvn3_to_unicode against tests/sample_tcvn3/sampletcvn3.txt."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.text.tcvn3 import tcvn3_to_unicode  # noqa: E402

SAMPLE = ROOT / "tests" / "sample_tcvn3" / "sampletcvn3.txt"


def main() -> int:
    failures = 0
    total = 0
    for lineno, line in enumerate(SAMPLE.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            print(f"line {lineno}: invalid format")
            failures += 1
            continue
        raw, expected = parts[0], parts[-1]
        total += 1
        got = tcvn3_to_unicode(raw)
        if got != expected:
            failures += 1
            print(f"FAIL line {lineno}")
            print(f"  raw: {raw!r}")
            print(f"  exp: {expected!r}")
            print(f"  got: {got!r}")
    print(f"{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
