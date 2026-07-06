"""Agent IV as an LLM reasoning brain (target design docs2/00, Sơ đồ 12).

This module turns Agent IV from a thin templated wrapper into a bounded
reasoning loop:

    DataProfiler -> AnalysisPlanner(LLM) -> [gate] -> SandboxRunner
                 -> ResultEvaluator(loop) -> ResponseAssembler

The loop is budget-limited by ``iv_max_steps``. Every executed step is gated
against the caller's ``PermissionsSnapshot`` (tool + function capability). On
any LLM/sandbox failure the caller (``DataAnalystService.decide``) falls back
to the deterministic ``analyze_datasets`` pipeline, so offline/CI runs and the
``ALLOW_LLM_STUB`` path keep working unchanged.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from project_core.domain.analysis.iv_analyzer import (
    _empty_feedback,
    _identifier_mismatch_feedback,
    _merge_external_paths,
)
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.feedback.analysis_tool_registry import apply_params_to_script

if TYPE_CHECKING:
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.contracts.workflow import PermissionsSnapshot
    from project_core.llm.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

# Substrings that must never appear in an LLM-authored analysis script. The
# sandbox subprocess already restricts builtins; this is a cheap first gate so
# obviously malicious code never reaches the child. Phase 5 hardens further.
_FORBIDDEN_SCRIPT_TOKENS: tuple[str, ...] = (
    "__import__",
    "importlib",
    "subprocess",
    "eval(",
    "exec(",
    "compile(",
    "globals(",
    "os.system",
    "os.popen",
    "socket",
    "open(",
    "Path(",
    "pd.read_sql",
    "read_html",
    "requests",
    "urllib",
)


def _sandbox():
    from python_sandbox import tools_impl

    return tools_impl


def _reject_unsafe_script(script: str) -> str | None:
    lowered = script.lower()
    for token in _FORBIDDEN_SCRIPT_TOKENS:
        if token.lower() in lowered:
            return f"forbidden_token:{token}"
    return None


class DataProfiler:
    """Compact, LLM-friendly profile of every resolved dataset."""

    def __init__(self, sandbox: Any) -> None:
        self._sandbox = sandbox

    def profile(self, paths: list[str], meta: list[dict[str, Any]]) -> list[dict[str, Any]]:
        profiles: list[dict[str, Any]] = []
        for idx, path in enumerate(paths):
            role = meta[idx].get("role") if idx < len(meta) else None
            entry: dict[str, Any] = {"index": idx, "role": role, "path": path}
            if not path or not Path(path).exists():
                entry["error"] = "missing"
                profiles.append(entry)
                continue
            loaded = self._sandbox.load_dataset(path)
            if "error" in loaded:
                entry["error"] = loaded["error"]
            else:
                entry["columns"] = loaded.get("columns", [])
                entry["row_count"] = loaded.get("row_count", 0)
                entry["sample"] = (loaded.get("preview") or [])[:5]
            profiles.append(entry)
        return profiles


class AnalysisPlanner:
    """One LLM turn: decide the next action given the running observation log."""

    def __init__(self, llm: "OpenRouterClient", profile_name: str, system_prompt: str) -> None:
        self._llm = llm
        self._profile_name = profile_name
        self._system_prompt = system_prompt
        self.tokens = 0

    def next_decision(self, state: dict[str, Any]) -> dict[str, Any]:
        result = self._llm.chat(
            profile_name=self._profile_name,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": json.dumps(state, ensure_ascii=False, default=str)},
            ],
            response_format={"type": "json_object"},
        )
        self.tokens += int(getattr(result, "usage_tokens", 0) or 0)
        return json.loads(result.content)


class SandboxRunner:
    """Executes a single planner-chosen step, enforcing capability gates."""

    def __init__(
        self,
        sandbox: Any,
        *,
        permissions: "PermissionsSnapshot",
        context_policy: "ContextPolicy",
        recipes_by_id: dict[str, dict[str, Any]],
    ) -> None:
        self._sandbox = sandbox
        self._perms = permissions
        self._cp = context_policy
        self._recipes = recipes_by_id

    def _gate_tool(self, tool_name: str) -> str | None:
        if not self._cp.can_invoke_tool(self._perms, "IV", tool_name):
            return f"tool_not_granted:{tool_name}"
        return None

    def run(self, step: dict[str, Any], paths: list[str], out_dir: str) -> dict[str, Any]:
        kind = str(step.get("kind") or "script")
        idx = int(step.get("dataset_index") or 0)
        dpath = paths[idx] if 0 <= idx < len(paths) else (paths[0] if paths else "")
        if not dpath or not Path(dpath).exists():
            return {"status": "error", "error": "missing_dataset", "kind": kind}

        if kind == "chart":
            return self._run_chart(step, dpath, out_dir)
        if kind == "excel":
            return self._run_excel(step, dpath, out_dir)
        if kind == "recipe":
            return self._run_recipe(step, dpath, out_dir)
        return self._run_script(step, dpath, out_dir)

    def _run_script(self, step: dict[str, Any], dpath: str, out_dir: str) -> dict[str, Any]:
        gate = self._gate_tool("run_analysis_script")
        if gate:
            return {"status": "policy_blocked", "error": gate, "kind": "script"}
        script = str(step.get("script") or "")
        if not script.strip():
            return {"status": "error", "error": "empty_script", "kind": "script"}
        unsafe = _reject_unsafe_script(script)
        if unsafe:
            return {"status": "policy_blocked", "error": unsafe, "kind": "script"}
        sub_out = str(Path(out_dir) / str(step.get("step_id") or "step"))
        Path(sub_out).mkdir(parents=True, exist_ok=True)
        result = self._sandbox.run_analysis_script(
            dpath, script, sub_out, tool_grants=list(self._perms.tool_grants)
        )
        return {"kind": "script", **result}

    def _run_chart(self, step: dict[str, Any], dpath: str, out_dir: str) -> dict[str, Any]:
        gate = self._gate_tool("plot_chart")
        if gate:
            return {"status": "policy_blocked", "error": gate, "kind": "chart"}
        chart = step.get("chart") or {}
        x = chart.get("x")
        y = chart.get("y")
        if not x or not y:
            return {"status": "error", "error": "chart_missing_axes", "kind": "chart"}
        out_path = str(Path(out_dir) / f"{step.get('step_id') or 'chart'}.png")
        result = self._sandbox.plot_chart(
            dpath, out_path, x, y, title=str(chart.get("title") or ""), kind=str(chart.get("kind") or "line")
        )
        return {"kind": "chart", **result}

    def _run_excel(self, step: dict[str, Any], dpath: str, out_dir: str) -> dict[str, Any]:
        gate = self._gate_tool("export_excel")
        if gate:
            return {"status": "policy_blocked", "error": gate, "kind": "excel"}
        out_path = str(Path(out_dir) / f"{step.get('step_id') or 'export'}.xlsx")
        result = self._sandbox.export_excel(dpath, out_path)
        return {"kind": "excel", **result}

    def _run_recipe(self, step: dict[str, Any], dpath: str, out_dir: str) -> dict[str, Any]:
        tool_id = str(step.get("tool_id") or "")
        gate = self._gate_tool("run_recipe_tool")
        if gate:
            return {"status": "policy_blocked", "error": gate, "kind": "recipe"}
        if not self._cp.can_invoke_function(self._perms, tool_id):
            return {"status": "policy_blocked", "error": f"function_not_granted:{tool_id}", "kind": "recipe"}
        recipe = self._recipes.get(tool_id)
        if not recipe:
            return {"status": "error", "error": f"recipe_not_found:{tool_id}", "kind": "recipe"}
        script = str(recipe.get("script_template") or "")
        steps = recipe.get("steps") or []
        if steps and not script:
            script = str((steps[0] or {}).get("script_template") or "")
        if not script:
            return {"status": "error", "error": f"recipe_no_script:{tool_id}", "kind": "recipe"}
        params = {**(recipe.get("params") or {}), **(step.get("params") or {})}
        script = apply_params_to_script(script, params)
        unsafe = _reject_unsafe_script(script)
        if unsafe:
            return {"status": "policy_blocked", "error": unsafe, "kind": "recipe"}
        sub_out = str(Path(out_dir) / f"recipe_{step.get('step_id') or tool_id}")
        Path(sub_out).mkdir(parents=True, exist_ok=True)
        result = self._sandbox.run_analysis_script(
            dpath, script, sub_out, tool_grants=list(self._perms.tool_grants)
        )
        return {"kind": "recipe", "tool_id": tool_id, **result}


def run_analysis_brain(
    *,
    brief: AnalysisBrief,
    manifest: dict[str, Any],
    profile: dict[str, Any],
    out_dir: str,
    max_steps: int,
    query_meta: list[dict[str, Any]] | None,
    recipe_candidates: list[dict[str, Any]] | None,
    domain_rules_excerpt: str,
    permissions: "PermissionsSnapshot",
    context_policy: "ContextPolicy",
    llm: "OpenRouterClient",
    profile_name: str,
    system_prompt: str,
) -> dict[str, Any]:
    """Run the bounded LLM reasoning loop and return an AnalystResponse payload."""
    sandbox = _sandbox()
    paths = [q.get("path") for q in manifest.get("queries", []) if q.get("path")]
    paths, meta = _merge_external_paths(brief, paths, query_meta or [])
    row_counts = {i: int(q.get("row_count", 0)) for i, q in enumerate(manifest.get("queries", []))}

    probe_idxs = [i for i, m in enumerate(meta) if m.get("role") == "probe"]
    main_idxs = [i for i, m in enumerate(meta) if m.get("role") != "probe"] or list(range(len(paths)))
    main_rows = sum(row_counts.get(i, 0) for i in main_idxs)
    probe_rows = sum(row_counts.get(i, 0) for i in probe_idxs)
    product_code = (brief.filters or {}).get("product_code") or (brief.filters or {}).get("sku")

    # Deterministic early exits (identical to the pipeline brain) before spending LLM budget.
    if main_rows == 0 and probe_rows > 0 and product_code:
        return _identifier_mismatch_feedback(str(product_code), probe_idxs, row_counts, paths)
    if profile.get("row_count", 0) == 0:
        return _empty_feedback(brief, product_code)

    profiler = DataProfiler(sandbox)
    dataset_profiles = profiler.profile([p for p in paths if p], [m for p, m in zip(paths, meta) if p])

    recipes_by_id = {str(c.get("tool_id")): c for c in (recipe_candidates or []) if c.get("tool_id")}
    planner = AnalysisPlanner(llm, profile_name, system_prompt)
    runner = SandboxRunner(
        sandbox, permissions=permissions, context_policy=context_policy, recipes_by_id=recipes_by_id
    )

    observations: list[dict[str, Any]] = []
    artifacts: list[str] = []
    chart_artifacts: list[str] = []
    excel_artifacts: list[str] = []
    steps_trace: list[dict[str, Any]] = []
    caveats: list[str] = []
    headline_metrics: dict[str, Any] = {"row_count": profile.get("row_count", 0)}
    steps_run = 0

    recipe_summaries = [
        {
            "tool_id": c.get("tool_id"),
            "name": c.get("name"),
            "intent_pattern": c.get("intent_pattern"),
            "score": c.get("score"),
        }
        for c in (recipe_candidates or [])
    ]

    terminal: dict[str, Any] | None = None
    while steps_run < max_steps:
        state = {
            "brief": brief.model_dump(),
            "domain_rules_excerpt": domain_rules_excerpt or "",
            "datasets": dataset_profiles,
            "recipe_candidates": recipe_summaries,
            "output_format": brief.output_format,
            "chart_spec": brief.chart_spec,
            "observations": observations,
            "steps_run": steps_run,
            "max_steps": max_steps,
            "remaining_steps": max_steps - steps_run,
        }
        try:
            decision = planner.next_decision(state)
        except Exception:
            logger.warning("IV planner LLM call failed at step %s", steps_run, exc_info=True)
            caveats.append("planner_failed")
            break

        action = str(decision.get("decision") or decision.get("action") or "finalize")

        if action == "data_feedback":
            fb = decision.get("data_feedback") or {}
            payload: dict[str, Any] = {"action": "data_feedback", "data_feedback": fb}
            if decision.get("suggest_clarify"):
                payload["suggest_clarify"] = decision["suggest_clarify"]
            payload["steps_trace"] = steps_trace
            return payload
        if action == "suggest_clarify":
            return {
                "action": "suggest_clarify",
                "clarification_request": decision.get("clarification_request")
                or decision.get("suggest_clarify")
                or {},
                "steps_trace": steps_trace,
            }
        if action == "impossible":
            return {
                "action": "impossible",
                "reason": decision.get("reason") or "metric_not_mappable",
                "impossible_reason": decision.get("impossible_reason") or "not_solvable_with_data",
                "explanation_vi": decision.get("insight_vi") or decision.get("explanation_vi"),
                "steps_trace": steps_trace,
            }
        if action in ("finalize", "complete", "partial"):
            terminal = decision
            break

        # action == run_step
        step = decision.get("step") or {}
        step.setdefault("step_id", f"iv-step-{steps_run + 1}")
        result = runner.run(step, [p for p in paths if p], out_dir)
        steps_run += 1
        status = result.get("status", "error")
        trace_entry = {
            "step_id": step.get("step_id"),
            "kind": result.get("kind"),
            "status": status,
            "thought": decision.get("thought"),
            "error": result.get("error"),
        }
        steps_trace.append(trace_entry)
        observations.append(
            {
                "step_id": step.get("step_id"),
                "kind": result.get("kind"),
                "status": status,
                "artifacts": result.get("artifacts") or ([result["path"]] if result.get("path") else []),
                "error": result.get("error"),
            }
        )
        if status == "ok":
            new_arts = result.get("artifacts") or ([result["path"]] if result.get("path") else [])
            artifacts.extend(new_arts)
            if result.get("kind") == "chart":
                chart_artifacts.extend(new_arts)
            elif result.get("kind") == "excel":
                excel_artifacts.extend(new_arts)
        else:
            caveats.append(f"{result.get('kind')}:{result.get('error')}")
    else:
        caveats.append("budget_exceeded")

    return _assemble_response(
        terminal=terminal,
        artifacts=artifacts,
        chart_artifacts=chart_artifacts,
        excel_artifacts=excel_artifacts,
        steps_trace=steps_trace,
        caveats=caveats,
        headline_metrics=headline_metrics,
        steps_run=steps_run,
        planner_tokens=planner.tokens,
    )


def _assemble_response(
    *,
    terminal: dict[str, Any] | None,
    artifacts: list[str],
    chart_artifacts: list[str],
    excel_artifacts: list[str],
    steps_trace: list[dict[str, Any]],
    caveats: list[str],
    headline_metrics: dict[str, Any],
    steps_run: int,
    planner_tokens: int,
) -> dict[str, Any]:
    """ResponseAssembler: map loop outcome to a complete/partial AnalystResponse."""
    status = "complete"
    insight_vi = None
    if terminal:
        status = str(terminal.get("status") or terminal.get("decision") or terminal.get("action") or "complete")
        if status not in ("complete", "partial"):
            status = "complete"
        fin = terminal.get("finalize") or terminal
        insight_vi = fin.get("insight_vi") or fin.get("explanation_vi") or terminal.get("insight_vi")
        headline_metrics = {**headline_metrics, **(fin.get("headline_metrics") or {})}
        caveats = caveats + list(fin.get("caveats") or [])

    has_success = bool(artifacts)
    if not terminal and not has_success:
        status = "partial"
    if any(c.startswith("planner_failed") for c in caveats) and not has_success:
        status = "partial"

    payload: dict[str, Any] = {
        "action": status,
        "headline_metrics": headline_metrics,
        "artifact_paths": artifacts,
        "chart_artifacts": chart_artifacts,
        "excel_artifacts": excel_artifacts,
        "caveats": caveats[:8],
        "sandbox_steps": steps_run,
        "steps_trace": steps_trace,
        "coverage": {
            "diagnosis": "full" if status == "complete" and has_success else "partial",
            "gaps": [c for c in caveats if ":" in c][:5],
        },
    }
    if insight_vi:
        payload["insight_vi"] = insight_vi
        payload["explanation_vi"] = insight_vi
    if planner_tokens:
        payload["usage_tokens"] = planner_tokens
    return payload
