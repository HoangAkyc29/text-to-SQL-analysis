from __future__ import annotations

import json
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
    safe_builtins = {"len": len, "str": str, "int": int, "float": float, "range": range, "open": open}
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


def run_recipe_tool(tool_id: str, path: str, output_dir: str, params_json: str = "{}") -> dict[str, Any]:
    """Invoke a promoted analysis recipe by tool_id (requires recipe registry wiring)."""
    try:
        from project_core.domain.analysis.recipe_runtime import get_registry

        reg = get_registry()
        if reg is None:
            return {"error": "recipe_registry_unavailable", "tool_id": tool_id}
        params = json.loads(params_json) if params_json else {}
        return reg.invoke_tool(tool_id, dataset_path=path, output_dir=output_dir, params=params)
    except Exception as exc:  # noqa: BLE001
        return {"error": "recipe_invoke_failed", "tool_id": tool_id, "detail": str(exc)}


def merge_datasets(primary_path: str, secondary_path: str, output_path: str, on: str = "") -> dict[str, Any]:
    """Join SQL dataset with external upload (parquet/csv) on shared key when possible."""
    left = pd.read_parquet(primary_path) if Path(primary_path).suffix == ".parquet" else pd.read_csv(primary_path)
    right = pd.read_parquet(secondary_path) if Path(secondary_path).suffix == ".parquet" else pd.read_csv(secondary_path)
    join_key = on or _guess_join_key(left.columns, right.columns)
    if join_key:
        merged = left.merge(right, on=join_key, how="left", suffixes=("", "_ext"))
    else:
        merged = pd.concat([left, right], axis=1)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix == ".parquet":
        merged.to_parquet(out, index=False)
    else:
        merged.to_csv(out, index=False)
    return {"status": "ok", "path": str(out), "row_count": len(merged), "join_key": join_key or None}


def _guess_join_key(left_cols: Any, right_cols: Any) -> str:
    preferred = ("SKU", "BARCODE", "STK_ID", "PRODUCT_CODE", "ITEM_CODE")
    left_set = {str(c).upper() for c in left_cols}
    right_set = {str(c).upper() for c in right_cols}
    for key in preferred:
        if key in left_set and key in right_set:
            for c in left_cols:
                if str(c).upper() == key:
                    return str(c)
    return ""
