"""Subprocess runner for constrained pandas analysis scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def main() -> int:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "usage", "detail": "runner_child.py <dataset_path> <output_dir>"}))
        return 2
    dataset_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    script = sys.stdin.read()
    if not script.strip():
        print(json.dumps({"error": "empty_script"}))
        return 2
    local_vars: dict = {
        "pd": pd,
        "plt": plt,
        "path": dataset_path,
        "out": output_dir,
    }
    safe_builtins = {"len": len, "str": str, "int": int, "float": float, "range": range, "min": min, "max": max}
    try:
        exec(script, {"__builtins__": safe_builtins}, local_vars)  # noqa: S102
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": "script_failed", "detail": str(exc)[:500]}))
        return 1
    artifacts = [str(p) for p in output_dir.iterdir() if p.is_file()]
    print(json.dumps({"status": "ok", "artifacts": artifacts}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
