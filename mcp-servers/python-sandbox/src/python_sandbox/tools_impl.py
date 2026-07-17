from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from project_core.domain.access.permission_set import grant_denial

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

_MAX_ROWS = int(os.getenv("SANDBOX_MAX_ROWS", "200000"))
_MAX_SECONDS = int(os.getenv("SANDBOX_MAX_SECONDS", "30"))
_RUNNER = Path(__file__).resolve().parent / "runner_child.py"


def _artifacts_root() -> Path:
    root = Path(os.getenv("ARTIFACTS_DIR", "data/artifacts")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _attachments_root() -> Path:
    return Path(os.getenv("ATTACHMENTS_DIR", "data/attachments")).resolve()


def _guard_input_path(path: str) -> tuple[Path | None, str | None]:
    p = Path(path).resolve()
    if not p.exists() or not p.is_file():
        return None, "file_not_found"
    for root in (_artifacts_root(), _attachments_root()):
        try:
            p.relative_to(root)
            return p, None
        except ValueError:
            continue
    return None, "path_not_allowed"


def _minimal_child_env() -> dict[str, str]:
    keep = {
        "PATH",
        "MPLBACKEND",
        "SYSTEMROOT",
        "SystemRoot",
        "SANDBOX_MAX_ROWS",
        "ARTIFACTS_DIR",
        "ATTACHMENTS_DIR",
    }
    env = {k: v for k, v in os.environ.items() if k in keep}
    env["MPLBACKEND"] = "Agg"
    env["SANDBOX_MAX_ROWS"] = str(_MAX_ROWS)
    env.setdefault("ARTIFACTS_DIR", str(_artifacts_root()))
    return env


def _guard_output_dir(output_dir: str) -> Path:
    out = Path(output_dir).resolve()
    root = _artifacts_root()
    try:
        out.relative_to(root)
    except ValueError as exc:
        raise ValueError("output_dir_must_be_under_artifacts_root") from exc
    out.mkdir(parents=True, exist_ok=True)
    return out


def load_dataset(path: str) -> dict[str, Any]:
    """Load parquet/csv dataset from artifact path."""
    p, err = _guard_input_path(path)
    if err:
        return {"error": err, "path": path}
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


def run_analysis_script(
    path: str,
    script: str,
    output_dir: str,
    tool_grants: list[str] | None = None,
) -> dict[str, Any]:
    """Execute constrained pandas script in an isolated subprocess.

    This is an internal compute primitive (also reused by the recipe runtime).
    Authorization is enforced upstream (Agent IV service + pipeline). When
    ``tool_grants`` is supplied — the untrusted MCP surface — the sandbox tool
    grant is re-checked here as defense-in-depth.
    """
    if tool_grants is not None:
        denied = grant_denial(
            tool_grants,
            "tool:python-sandbox:run_analysis_script",
            "tool_not_granted:python-sandbox:run_analysis_script",
        )
        if denied is not None:
            return denied
    try:
        out = _guard_output_dir(output_dir)
    except ValueError as exc:
        return {"error": str(exc)}
    dataset, err = _guard_input_path(path)
    if err:
        return {"error": err, "path": path}
    child_env = _minimal_child_env()
    proc = subprocess.run(
        [sys.executable, str(_RUNNER), str(dataset), str(out)],
        input=script,
        capture_output=True,
        text=True,
        timeout=_MAX_SECONDS,
        cwd=str(out),
        env=child_env,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        try:
            payload = json.loads(proc.stdout.strip() or "{}")
            if "error" in payload:
                payload.setdefault("status", "error")
                return payload
            return {"status": "error", "error": "script_failed", "detail": detail[:500]}
        except json.JSONDecodeError:
            return {"status": "error", "error": "script_failed", "detail": detail[:500]}
    try:
        payload = json.loads(proc.stdout.strip() or "{}")
    except json.JSONDecodeError:
        artifacts = [str(p) for p in out.glob("*") if p.is_file()]
        return {"status": "ok", "artifacts": artifacts}
    if not isinstance(payload, dict):
        return {"status": "error", "error": "invalid_runner_payload"}
    payload.setdefault("status", "ok" if "error" not in payload else "error")
    return payload


def export_excel(path: str, output_path: str) -> dict[str, Any]:
    """Export dataset to Excel."""
    src, err = _guard_input_path(path)
    if err:
        return {"error": err, "path": path}
    out_p = Path(output_path).resolve()
    try:
        out_p.relative_to(_artifacts_root())
    except ValueError:
        return {"error": "output_path_must_be_under_artifacts_root", "path": output_path}
    out_p.parent.mkdir(parents=True, exist_ok=True)
    loaded = load_dataset(path)
    if "error" in loaded:
        return loaded
    df = pd.read_parquet(src) if src.suffix == ".parquet" else pd.read_csv(src)
    if len(df) > _MAX_ROWS:
        df = df.head(_MAX_ROWS)
    df.to_excel(out_p, index=False)
    return {"status": "ok", "path": str(out_p)}


def plot_chart(
    path: str,
    output_path: str,
    x: str,
    y: str,
    title: str = "",
    kind: str = "line",
) -> dict[str, Any]:
    """Create a line/bar/pie chart from dataset columns.

    ``kind`` selects the chart type (``line`` default, ``bar``, ``pie``). Falls
    back to a line chart for unknown kinds.
    """
    src, err = _guard_input_path(path)
    if err:
        return {"error": err, "path": path}
    out_p = Path(output_path).resolve()
    try:
        out_p.relative_to(_artifacts_root())
    except ValueError:
        return {"error": "output_path_must_be_under_artifacts_root", "path": output_path}
    out_p.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(src) if src.suffix == ".parquet" else pd.read_csv(src)
    if len(df) > _MAX_ROWS:
        df = df.head(_MAX_ROWS)
    if x not in df.columns or y not in df.columns:
        return {"error": "column_not_found", "x": x, "y": y}
    kind = (kind or "line").lower()
    plt.figure(figsize=(10, 6))
    try:
        if kind == "bar":
            plt.bar(df[x].astype(str), df[y])
        elif kind == "pie":
            plt.pie(df[y], labels=df[x].astype(str), autopct="%1.1f%%")
        else:
            plt.plot(df[x], df[y])
        if title:
            plt.title(title)
        plt.tight_layout()
        plt.savefig(out_p)
    finally:
        plt.close()
    return {"status": "ok", "path": str(out_p), "kind": kind}


def run_recipe_tool(
    tool_id: str,
    path: str,
    output_dir: str,
    params_json: str = "{}",
    allowed_functions: list[str] | None = None,
) -> dict[str, Any]:
    """Invoke a promoted analysis recipe by tool_id (requires recipe registry wiring).

    When ``allowed_functions`` is supplied (untrusted MCP surface), the function
    capability is re-checked as defense-in-depth (``function:<tool_id>`` or
    ``function:*``); the authoritative gate is the pipeline / Agent IV service.
    """
    if allowed_functions is not None:
        denied = grant_denial(
            allowed_functions,
            f"function:{tool_id}",
            f"function_not_granted:{tool_id}",
        )
        if denied is not None:
            return {**denied, "tool_id": tool_id}
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
    left_p, err = _guard_input_path(primary_path)
    if err:
        return {"error": err, "path": primary_path}
    right_p, err2 = _guard_input_path(secondary_path)
    if err2:
        return {"error": err2, "path": secondary_path}
    out_p = Path(output_path).resolve()
    try:
        out_p.relative_to(_artifacts_root())
    except ValueError:
        return {"error": "output_path_must_be_under_artifacts_root", "path": output_path}
    left = pd.read_parquet(left_p) if left_p.suffix == ".parquet" else pd.read_csv(left_p)
    right = pd.read_parquet(right_p) if right_p.suffix == ".parquet" else pd.read_csv(right_p)
    if len(left) > _MAX_ROWS:
        left = left.head(_MAX_ROWS)
    if len(right) > _MAX_ROWS:
        right = right.head(_MAX_ROWS)
    join_key = on or _guess_join_key(left.columns, right.columns)
    if join_key:
        merged = left.merge(right, on=join_key, how="left", suffixes=("", "_ext"))
    else:
        merged = pd.concat([left, right], axis=1)
    out = out_p
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
