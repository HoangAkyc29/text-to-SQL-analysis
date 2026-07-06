"""Subprocess runner for constrained pandas analysis scripts."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

_MAX_ROWS = int(os.environ.get("SANDBOX_MAX_ROWS", "200000"))


def _cap_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.head(_MAX_ROWS) if len(df) > _MAX_ROWS else df


def _guard_dataset_path(path: Path) -> bool:
    roots = [
        Path(os.environ.get("ARTIFACTS_DIR", "data/artifacts")).resolve(),
        Path(os.environ.get("ATTACHMENTS_DIR", "data/attachments")).resolve(),
    ]
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def main() -> int:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "usage", "detail": "runner_child.py <dataset_path> <output_dir>"}))
        return 2
    dataset_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    if not _guard_dataset_path(dataset_path):
        print(json.dumps({"error": "path_not_allowed", "path": str(dataset_path)}))
        return 2
    artifacts_root = Path(os.environ.get("ARTIFACTS_DIR", "data/artifacts")).resolve()
    try:
        output_dir.relative_to(artifacts_root)
    except ValueError:
        print(json.dumps({"error": "output_dir_must_be_under_artifacts_root"}))
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)
    script = sys.stdin.read()
    if not script.strip():
        print(json.dumps({"error": "empty_script"}))
        return 2
    _orig_read_parquet = pd.read_parquet
    _orig_read_csv = pd.read_csv

    def _safe_read_parquet(*args, **kwargs):
        return _cap_df(_orig_read_parquet(*args, **kwargs))

    def _safe_read_csv(*args, **kwargs):
        return _cap_df(_orig_read_csv(*args, **kwargs))

    pd.read_parquet = _safe_read_parquet  # type: ignore[method-assign]
    pd.read_csv = _safe_read_csv  # type: ignore[method-assign]
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
