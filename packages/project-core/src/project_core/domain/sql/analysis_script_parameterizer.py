from __future__ import annotations

import re
from typing import Any


def parameterize_analysis_script(script: str) -> str:
    out = script
    out = re.sub(r"/[^\s'\"]+\.parquet", ":dataset_path", out)
    out = re.sub(r"/[^\s'\"]+/out", ":output_dir", out)
    return out


def build_tool_record(
    *,
    name: str,
    intent_pattern: str,
    script: str,
    input_schema: dict[str, Any],
    output_schema: dict[str, Any],
    trace_id: str,
    sql_dependencies: list[str] | None = None,
    parent_tool_id: str | None = None,
    steps: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from uuid import uuid4

    version = 1
    if parent_tool_id:
        version = 2
    return {
        "tool_id": str(uuid4()),
        "name": name,
        "status": "staged",
        "kind": "recipe" if steps and len(steps) > 1 else "script",
        "intent_pattern": intent_pattern,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "script_template": parameterize_analysis_script(script),
        "steps": steps or [],
        "sql_dependencies": sql_dependencies or [],
        "parent_tool_id": parent_tool_id,
        "version": version,
        "source_trace_id": trace_id,
        "promote_score": 0.0,
    }
