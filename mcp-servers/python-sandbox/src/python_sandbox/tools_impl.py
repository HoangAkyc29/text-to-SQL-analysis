from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

_MAX_ROWS = int(os.getenv("SANDBOX_MAX_ROWS", "200000"))
_MAX_SECONDS = int(os.getenv("SANDBOX_MAX_SECONDS", "30"))


def _limit_resources() -> None:
    if sys.platform == "win32":
        return
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (_MAX_SECONDS, _MAX_SECONDS))


def load_dataset(path: str) -> dict[str, Any]:
    """Load parquet/csv dataset from artifact path."""
    p = Path(path)
    if not p.exists():
        return {"error": "file_not_found", "path": path}
    if p.suffix == ".parquet":
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p)
    if len(df) > _MAX_ROWS:
        df = df.head(_MAX_ROWS)
    return {"columns": list(df.columns.astype(str)), "row_count": len(df), "preview": df.head(20).to_dict(orient="records")}


def preview_dataframe(path: str, n: int = 100) -> dict[str, Any]:
    """Return head of dataframe."""
    loaded = load_dataset(path)
    if "error" in loaded:
        return loaded
    return {"preview": loaded.get("preview", [])[:n]}


def run_analysis_script(path: str, script: str, output_dir: str) -> dict[str, Any]:
    """Execute constrained pandas script against dataset path."""
    _limit_resources()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    local_vars: dict[str, Any] = {"pd": pd, "plt": plt, "path": path, "out": out}
    safe_builtins = {"len": len, "str": str, "int": int, "float": float, "range": range}
    exec(script, {"__builtins__": safe_builtins}, local_vars)  # noqa: S102
    artifacts = [str(p) for p in out.glob("*")]
    return {"status": "ok", "artifacts": artifacts}


def export_excel(path: str, output_path: str) -> dict[str, Any]:
    """Export dataset to Excel."""
    loaded = load_dataset(path)
    if "error" in loaded:
        return loaded
    df = pd.read_parquet(path) if Path(path).suffix == ".parquet" else pd.read_csv(path)
    df.to_excel(output_path, index=False)
    return {"status": "ok", "path": output_path}


def plot_chart(path: str, output_path: str, x: str, y: str, title: str = "") -> dict[str, Any]:
    """Create simple line/bar chart from dataset columns."""
    df = pd.read_parquet(path) if Path(path).suffix == ".parquet" else pd.read_csv(path)
    plt.figure(figsize=(10, 6))
    plt.plot(df[x], df[y])
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return {"status": "ok", "path": output_path}
