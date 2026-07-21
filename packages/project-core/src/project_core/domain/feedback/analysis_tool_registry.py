from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from project_core.domain.analysis.recipe_matcher import rank_candidates
from project_core.domain.analysis.recipe_retriever import hybrid_rank_candidates
from project_core.domain.contracts.analysis_plan import RecipeCandidate, RecipeStep
from project_core.domain.sql.analysis_script_parameterizer import build_tool_record


def _clean_op_chain(steps: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for raw in steps or []:
        if not isinstance(raw, dict) or not raw.get("op_id"):
            continue
        # Runtime observations are not reusable recipe steps.
        if raw.get("status") is not None and not any(
            key in raw for key in ("args", "dataset", "save_as")
        ):
            continue
        step: dict[str, Any] = {
            "op_id": str(raw["op_id"]),
            "args": dict(raw.get("args") or {}),
        }
        if raw.get("dataset") is not None:
            step["dataset"] = raw["dataset"]
        if raw.get("save_as") is not None:
            step["save_as"] = raw["save_as"]
        cleaned.append(step)
    return cleaned


def apply_params_to_script(script: str, params: dict[str, Any]) -> str:
    out = script
    for key, value in params.items():
        out = out.replace(f"params['{key}']", json.dumps(value))
        out = out.replace(f'params["{key}"]', json.dumps(value))
        out = out.replace(f":param_{key}", json.dumps(value))
    return out


class AnalysisToolRegistry:
    def __init__(self, collection: Any, *, embed_fn: Any | None = None) -> None:
        self.collection = collection
        self.embed_fn = embed_fn

    def find_promoted(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self.collection.find({"status": "promoted"}).limit(limit))

    def _query_embedding(self, intent: str) -> list[float] | None:
        if not self.embed_fn:
            return None
        try:
            emb = self.embed_fn(intent)
            return emb if isinstance(emb, list) and emb else None
        except Exception:
            return None

    def _attach_embedding(self, record: dict[str, Any]) -> dict[str, Any]:
        text = record.get("intent_pattern") or record.get("name") or ""
        emb = self._query_embedding(text)
        if emb:
            record["embedding"] = emb
        return record

    def find_candidates(self, intent: str, *, top_k: int = 5) -> list[RecipeCandidate]:
        tools = self.find_promoted(limit=100)
        q_emb = self._query_embedding(intent)
        if q_emb:
            return hybrid_rank_candidates(intent, tools, query_embedding=q_emb, top_k=top_k)
        return rank_candidates(intent, tools, top_k=top_k)

    def find_similar_intent(self, intent: str, *, threshold: float = 0.85) -> dict[str, Any] | None:
        for cand in self.find_candidates(intent, top_k=3):
            if cand.score >= threshold:
                existing = self.collection.find_one({"tool_id": cand.tool_id})
                if existing:
                    return existing
        return None

    def stage_from_run(
        self,
        *,
        name: str,
        intent: str,
        script: str,
        trace_id: str,
        datasets: list[dict[str, Any]],
        artifacts: list[str],
        metrics: dict[str, Any],
        params: list[dict[str, Any]] | None = None,
        steps: list[dict[str, Any]] | None = None,
        verification: dict[str, Any] | None = None,
        parent_tool_id: str | None = None,
    ) -> str:
        if not steps and self.find_similar_intent(intent):
            return str(self.find_similar_intent(intent)["tool_id"])

        clean_chain = _clean_op_chain(steps)
        record = build_tool_record(
            name=name,
            intent_pattern=intent,
            script=script,
            input_schema={"datasets": datasets, "params": params or []},
            output_schema={"artifacts": artifacts, "metrics": list(metrics.keys())},
            trace_id=trace_id,
            parent_tool_id=parent_tool_id,
            steps=clean_chain or None,
        )
        if steps is not None:
            record["kind"] = "catalog_op_chain"
            record["op_chain"] = clean_chain
            record["verification_semantics"] = {
                "has_export": any(
                    step["op_id"] in {"export_csv", "export_excel", "plot_chart"}
                    for step in clean_chain
                ),
                "verified": bool(
                    verification
                    and verification.get("status") == "passed"
                    and verification.get("revision") is not None
                ),
            }
        record["created_at"] = datetime.utcnow()
        record = self._attach_embedding(record)
        self.collection.update_one({"tool_id": record["tool_id"]}, {"$set": record}, upsert=True)
        return record["tool_id"]

    def stage_step(
        self,
        *,
        step: RecipeStep,
        intent: str,
        trace_id: str,
        parent_tool_id: str | None = None,
    ) -> str:
        record = build_tool_record(
            name=step.name or step.step_id,
            intent_pattern=intent,
            script=step.script_template,
            input_schema={"datasets": [], "params": [p.model_dump() for p in step.param_schema]},
            output_schema={"artifacts": [], "metrics": []},
            trace_id=trace_id,
            parent_tool_id=parent_tool_id or step.source_tool_id,
            steps=[step.model_dump()],
        )
        record["kind"] = "step"
        record["created_at"] = datetime.utcnow()
        record = self._attach_embedding(record)
        self.collection.update_one({"tool_id": record["tool_id"]}, {"$set": record}, upsert=True)
        return record["tool_id"]

    def promote(self, tool_id: str) -> None:
        tool = self.collection.find_one({"tool_id": tool_id})
        if tool and tool.get("kind") == "catalog_op_chain":
            semantics = tool.get("verification_semantics") or {}
            if not tool.get("op_chain") or not semantics.get("has_export") or not semantics.get("verified"):
                raise ValueError("catalog_recipe_requires_verified_export_semantics")
        self.collection.update_one(
            {"tool_id": tool_id},
            {"$set": {"status": "promoted", "promote_score": 1.0, "promoted_at": datetime.utcnow()}},
        )

    def demote(self, tool_id: str) -> None:
        self.collection.update_one(
            {"tool_id": tool_id},
            {"$set": {"status": "demoted", "demoted_at": datetime.utcnow()}},
        )

    def bump_promote_score(self, tool_id: str, delta: float) -> None:
        tool = self.collection.find_one({"tool_id": tool_id})
        if not tool:
            return
        new_score = float(tool.get("promote_score", 0)) + delta
        self.collection.update_one({"tool_id": tool_id}, {"$set": {"promote_score": new_score}})
        if new_score >= 1.0:
            self.promote(tool_id)

    def find_by_trace(self, trace_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"source_trace_id": trace_id})

    def list_mcp_tool_descriptors(self, *, limit: int = 30) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for tool in self.find_promoted(limit=limit):
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(tool.get("name") or tool.get("tool_id")))[:48]
            params = (tool.get("input_schema") or {}).get("params") or []
            out.append(
                {
                    "name": f"recipe_{safe_name}",
                    "tool_id": str(tool.get("tool_id")),
                    "description": str(tool.get("intent_pattern") or tool.get("name") or ""),
                    "params": params,
                }
            )
        return out

    def stage_op_chain(
        self,
        *,
        name: str,
        intent: str,
        op_chain: list[dict[str, Any]],
        trace_id: str,
        datasets: list[dict[str, Any]] | None = None,
        artifacts: list[str] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> str:
        """Stage a catalog op-chain recipe (preferred over script recipes)."""
        if self.find_similar_intent(intent):
            return str(self.find_similar_intent(intent)["tool_id"])
        record = build_tool_record(
            name=name,
            intent_pattern=intent,
            script="",
            input_schema={"datasets": datasets or [], "params": []},
            output_schema={"artifacts": artifacts or [], "metrics": list((metrics or {}).keys())},
            trace_id=trace_id,
            steps=op_chain,
        )
        record["created_at"] = datetime.utcnow()
        record = self._attach_embedding(record)
        self.collection.update_one({"tool_id": record["tool_id"]}, {"$set": record}, upsert=True)
        return record["tool_id"]

    def invoke_tool(
        self,
        tool_id: str,
        *,
        dataset_path: str,
        output_dir: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tool = self.collection.find_one({"tool_id": tool_id})
        if not tool:
            return {"error": "tool_not_found", "tool_id": tool_id}
        steps = tool.get("op_chain") or tool.get("steps") or []
        if steps and all(isinstance(s, dict) and s.get("op_id") for s in steps):
            from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op

            ws = DatasetWorkingSet.from_manifest(
                {"queries": [{"path": dataset_path, "ref": "q0"}]},
                [{"role": "main"}],
                work_dir=str(Path(output_dir) / "_ws"),
            )
            for step in steps:
                args = dict(step.get("args") or {})
                args.update(params or {})
                if step.get("dataset") and "dataset" not in args:
                    args["dataset"] = step["dataset"]
                if "dataset" not in args:
                    args["dataset"] = "q0"
                if step.get("save_as"):
                    args["save_as"] = step["save_as"]
                res = execute_op(ws, str(step["op_id"]), args, out_dir=output_dir)
                if res.status != "ok":
                    return {"status": "error", "error": res.error, "op_id": step["op_id"]}
            return {"status": "ok", "artifacts": list(ws.artifact_paths)}
        if steps:
            step = RecipeStep.model_validate(steps[0])
        else:
            step = RecipeStep(
                step_id=f"{tool_id}-main",
                name=str(tool.get("name") or tool_id),
                script_template=str(tool.get("script_template") or ""),
                source_tool_id=tool_id,
                status="reuse",
            )
        return self.invoke_step(step, dataset_path=dataset_path, output_dir=output_dir, params=params)

    def invoke_step(
        self,
        step: RecipeStep | dict[str, Any],
        *,
        dataset_path: str,
        output_dir: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from python_sandbox import tools_impl

        if isinstance(step, RecipeStep):
            script = step.script_template
            params = {**step.params, **(params or {})}
        else:
            script = step.get("script_template", "")
            params = params or step.get("params") or {}
        script = apply_params_to_script(script, params)
        script = script.replace(":dataset_path", dataset_path).replace(":output_dir", output_dir)
        return tools_impl.run_analysis_script(dataset_path, script, output_dir)
