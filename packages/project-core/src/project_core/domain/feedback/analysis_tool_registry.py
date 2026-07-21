from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from project_core.domain.analysis.recipe_binding import (
    bind_and_preflight,
    canonicalize_op_chain,
    is_recipe_v2,
    resolve_runtime_args,
)
from project_core.domain.analysis.ops.registry import list_op_ids
from project_core.domain.analysis.recipe_retriever import hybrid_rank_candidates
from project_core.domain.contracts.analysis_plan import (
    RecipeCandidate,
    RecipeDatasetContract,
    RecipeStep,
    RecipeVerificationContract,
)
from project_core.domain.sql.analysis_script_parameterizer import build_tool_record


def _clean_op_chain(steps: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return canonicalize_op_chain(steps)


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
        query = {
            "status": "promoted",
            "kind": "catalog_op_chain",
            "compatibility_version": 2,
        }
        cursor = self.collection.find(query)
        tools = list(cursor.limit(limit)) if hasattr(cursor, "limit") else list(cursor)[:limit]
        return [tool for tool in tools if is_recipe_v2(tool)]

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

    def find_candidates(
        self,
        intent: str,
        *,
        top_k: int = 5,
        datasets: list[dict[str, Any]] | None = None,
        params: dict[str, Any] | None = None,
        available_ops: set[str] | None = None,
        min_score: float = 0.2,
        rejected: list[RecipeCandidate] | None = None,
    ) -> list[RecipeCandidate]:
        tools = self.find_promoted(limit=100)
        q_emb = self._query_embedding(intent)
        return hybrid_rank_candidates(
            intent,
            tools,
            query_embedding=q_emb,
            top_k=top_k,
            token_weight=0.45 if q_emb else 1.0,
            embed_weight=0.55 if q_emb else 0.0,
            datasets=datasets,
            params=params,
            available_ops=available_ops,
            min_score=min_score,
            rejected=rejected,
        )

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
        clean_chain = _clean_op_chain(steps)
        if not clean_chain:
            raise ValueError("recipe_v2_requires_catalog_op_chain")
        unavailable = [
            step["op_id"]
            for step in clean_chain
            if step["op_id"] not in set(list_op_ids())
        ]
        if unavailable:
            raise ValueError(f"recipe_v2_unknown_ops:{sorted(set(unavailable))}")
        dataset_contracts = _coerce_dataset_contracts(datasets)
        clean_chain = _parameterize_dataset_and_artifact_refs(
            clean_chain,
            datasets=datasets,
            contracts=dataset_contracts,
        )
        verification_contract = _verification_contract(verification)
        record = build_tool_record(
            name=name,
            intent_pattern=intent,
            script="",
            input_schema={"datasets": datasets, "params": params or []},
            output_schema={"artifacts": artifacts, "metrics": list(metrics.keys())},
            trace_id=trace_id,
            parent_tool_id=parent_tool_id,
            steps=clean_chain,
        )
        record.update(
            {
                "kind": "catalog_op_chain",
                "compatibility_version": 2,
                "script_template": "",
                "op_chain": clean_chain,
                "steps": clean_chain,
                "dataset_contracts": [c.model_dump() for c in dataset_contracts],
                "param_schema": list(params or []),
                "verification_contract": verification_contract.model_dump(),
                "source_verification": dict(verification or {}),
            }
        )
        record["created_at"] = datetime.now(UTC)
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
        raise ValueError("legacy_recipe_steps_are_not_supported")

    def promote(self, tool_id: str) -> None:
        tool = self.collection.find_one({"tool_id": tool_id})
        if not tool:
            raise ValueError("tool_not_found")
        if not is_recipe_v2(tool):
            raise ValueError("only_canonical_recipe_v2_can_be_promoted")
        verification = RecipeVerificationContract.model_validate(
            tool.get("verification_contract") or {}
        )
        missing_ops = set(verification.required_ops) - {
            step["op_id"] for step in canonicalize_op_chain(tool.get("op_chain"))
        }
        if missing_ops:
            raise ValueError(f"recipe_missing_verification_ops:{sorted(missing_ops)}")
        if not verification.source_run_verified:
            raise ValueError("recipe_source_run_not_verified")
        if not verification.replay_verified:
            raise ValueError("recipe_deterministic_replay_not_verified")
        self.collection.update_one(
            {"tool_id": tool_id},
            {
                "$set": {
                    "status": "promoted",
                    "promote_score": 1.0,
                    "promoted_at": datetime.now(UTC),
                }
            },
        )

    def demote(self, tool_id: str) -> None:
        self.collection.update_one(
            {"tool_id": tool_id},
            {"$set": {"status": "demoted", "demoted_at": datetime.now(UTC)}},
        )

    def bump_promote_score(self, tool_id: str, delta: float) -> None:
        tool = self.collection.find_one({"tool_id": tool_id})
        if not tool:
            return
        new_score = float(tool.get("promote_score", 0)) + delta
        self.collection.update_one({"tool_id": tool_id}, {"$set": {"promote_score": new_score}})
        if new_score >= 1.0:
            try:
                self.promote(tool_id)
            except ValueError:
                # Feedback changes confidence, never verification state.
                return

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
        params: list[dict[str, Any]] | None = None,
        verification: dict[str, Any] | None = None,
    ) -> str:
        """Stage a catalog op-chain recipe (preferred over script recipes)."""
        return self.stage_from_run(
            name=name,
            intent=intent,
            script="",
            trace_id=trace_id,
            datasets=datasets or [],
            artifacts=artifacts or [],
            metrics=metrics or {},
            params=params,
            steps=op_chain,
            verification=verification,
        )

    def invoke_tool(
        self,
        tool_id: str,
        *,
        dataset_path: str = "",
        datasets: list[dict[str, Any]] | None = None,
        output_dir: str,
        params: dict[str, Any] | None = None,
        record_replay: bool = True,
    ) -> dict[str, Any]:
        tool = self.collection.find_one({"tool_id": tool_id})
        if not tool:
            return {"error": "tool_not_found", "tool_id": tool_id}
        if not is_recipe_v2(tool):
            return {"status": "error", "error": "recipe_not_canonical_v2"}

        from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op

        supplied = list(datasets or [])
        if dataset_path and not supplied:
            contracts = tool.get("dataset_contracts") or []
            role = str(contracts[0].get("role") if contracts else "primary")
            supplied = [{"ref": "q0", "path": dataset_path, "role": role}]
        manifest_queries = [
            {
                "path": ds.get("path"),
                "ref": ds.get("ref") or f"q{i}",
                "role": ds.get("role"),
                "format": ds.get("format"),
            }
            for i, ds in enumerate(supplied)
        ]
        ws = DatasetWorkingSet.from_manifest(
            {"queries": manifest_queries},
            [{"role": ds.get("role")} for ds in supplied],
            work_dir=str(Path(output_dir) / "_ws"),
        )
        profiled = []
        for supplied_ds, profile in zip(supplied, ws.list_profiles()):
            profiled.append(
                {
                    **supplied_ds,
                    "ref": profile["ref"],
                    "columns": profile.get("columns") or supplied_ds.get("columns") or [],
                    "dtypes": profile.get("dtypes") or supplied_ds.get("dtypes") or {},
                }
            )
        preflight = bind_and_preflight(
            tool,
            profiled,
            params=params,
            available_ops=set(list_op_ids()),
        )
        if not preflight.compatible:
            return {
                "status": "error",
                "error": "recipe_preflight_failed",
                "rejection_reasons": preflight.rejection_reasons,
            }

        outputs: dict[str, Any] = {}
        observations: list[dict[str, Any]] = []
        executed_ops: list[str] = []
        for index, step in enumerate(preflight.op_chain):
            try:
                args = resolve_runtime_args(
                    step["args"],
                    dataset_bindings=preflight.dataset_bindings,
                    params=params or {},
                    outputs=outputs,
                )
            except ValueError as exc:
                return {"status": "error", "error": f"recipe_binding_failed:{exc}"}
            res = execute_op(ws, str(step["op_id"]), args, out_dir=output_dir)
            observation = res.as_observation()
            observations.append(observation)
            if res.status != "ok":
                return {
                    "status": "error",
                    "error": res.error,
                    "op_id": step["op_id"],
                    "observations": observations,
                }
            executed_ops.append(str(step["op_id"]))
            output_name = str(step.get("output") or f"step{index}")
            outputs[output_name] = res.result
            for key, value in res.result.items():
                outputs[f"{output_name}.{key}"] = value

        verification = RecipeVerificationContract.model_validate(
            tool.get("verification_contract") or {}
        )
        post_errors = _verify_replay_artifacts(ws, verification, executed_ops)
        if post_errors:
            return {
                "status": "error",
                "error": "post_replay_verification_failed",
                "rejection_reasons": post_errors,
                "observations": observations,
            }
        if record_replay:
            updated_verification = verification.model_copy(
                update={"replay_verified": True}
            )
            self.collection.update_one(
                {"tool_id": tool_id},
                {
                    "$set": {
                        "verification_contract": updated_verification.model_dump(),
                        "last_replay_at": datetime.now(UTC),
                    }
                },
            )
        return {
            "status": "ok",
            "artifacts": list(ws.artifact_paths),
            "primary_artifacts": list(ws.primary_artifacts),
            "dataset_bindings": preflight.dataset_bindings,
            "observations": observations,
        }

    def invoke_step(
        self,
        step: RecipeStep | dict[str, Any],
        *,
        dataset_path: str,
        output_dir: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {"status": "error", "error": "legacy_script_runtime_not_supported"}


def _coerce_dataset_contracts(
    datasets: list[dict[str, Any]],
) -> list[RecipeDatasetContract]:
    contracts: list[RecipeDatasetContract] = []
    used_roles: set[str] = set()
    for index, raw in enumerate(datasets):
        base_role = str(raw.get("role") or f"dataset_{index}")
        role = base_role
        if role in used_roles:
            role = f"{base_role}_{index}"
        used_roles.add(role)
        contract = {
            "role": role,
            "required_columns": raw.get("required_columns") or raw.get("columns") or [],
            "optional_columns": raw.get("optional_columns") or [],
            "dtypes": raw.get("dtypes") or {},
            "grain": raw.get("grain") or [],
            "source_kind": raw.get("source_kind"),
        }
        contracts.append(RecipeDatasetContract.model_validate(contract))
    if not contracts:
        raise ValueError("recipe_v2_requires_dataset_contracts")
    return contracts


def _parameterize_dataset_and_artifact_refs(
    chain: list[dict[str, Any]],
    *,
    datasets: list[dict[str, Any]],
    contracts: list[RecipeDatasetContract],
) -> list[dict[str, Any]]:
    """Convert run-local refs into deterministic role/output templates."""
    ref_to_template: dict[str, str] = {}
    for index, (raw, contract) in enumerate(zip(datasets, contracts, strict=True)):
        ref = str(raw.get("ref") or f"q{index}")
        ref_to_template[ref] = f"{{{{dataset.{contract.role}}}}}"
        # SQL query manifests conventionally expose q{index}; preserve that
        # alias even when a richer source ref was supplied.
        ref_to_template.setdefault(f"q{index}", f"{{{{dataset.{contract.role}}}}}")

    output_by_artifact_id: dict[str, str] = {}
    last_artifact_output = ""
    parameterized: list[dict[str, Any]] = []
    for index, step in enumerate(chain):
        op_id = str(step["op_id"])
        args = _replace_dataset_refs(dict(step.get("args") or {}), ref_to_template)
        output_name = str(step.get("output") or f"step{index}")
        if op_id in {"export_csv", "export_excel", "plot_chart"}:
            output_name = f"artifact_{index}"
            last_artifact_output = output_name
            artifact_id = str(args.pop("artifact_id", "") or "")
            if artifact_id:
                output_by_artifact_id[artifact_id] = output_name
        elif op_id in {"validate_export", "reload_artifact"}:
            artifact_id = str(args.get("artifact_id") or "")
            artifact_output = output_by_artifact_id.get(artifact_id) or last_artifact_output
            if artifact_output:
                args["artifact_id"] = f"{{{{output.{artifact_output}.artifact_id}}}}"
        parameterized.append({"op_id": op_id, "args": args, "output": output_name})
    return parameterized


def _replace_dataset_refs(value: Any, refs: dict[str, str]) -> Any:
    if isinstance(value, str):
        return refs.get(value, value)
    if isinstance(value, list):
        return [_replace_dataset_refs(item, refs) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_dataset_refs(item, refs)
            for key, item in value.items()
        }
    return value


def _verification_contract(
    verification: dict[str, Any] | None,
) -> RecipeVerificationContract:
    raw = dict(verification or {})
    source_verified = bool(
        raw.get("source_run_verified")
        or (
            raw.get("status") == "passed"
            and raw.get("revision") is not None
        )
    )
    return RecipeVerificationContract(
        required_ops=list(raw.get("required_ops") or ["validate_export"]),
        require_primary_artifact=bool(raw.get("require_primary_artifact", True)),
        require_current_revision=bool(raw.get("require_current_revision", True)),
        source_run_verified=source_verified,
        replay_verified=bool(raw.get("replay_verified", False)),
    )


def _verify_replay_artifacts(
    ws: Any,
    contract: RecipeVerificationContract,
    executed_ops: list[str],
) -> list[str]:
    reasons: list[str] = []
    for op_id in contract.required_ops:
        if op_id not in executed_ops:
            reasons.append(f"required_verification_op_not_executed:{op_id}")
    if contract.require_primary_artifact and not ws.primary_artifacts:
        reasons.append("primary_artifact_missing")
    for artifact in ws.artifacts.values():
        path = Path(artifact.path)
        if not path.exists() or not path.is_file() or path.stat().st_size <= 0:
            reasons.append(f"artifact_invalid:{artifact.filename}")
        if artifact.validation_status != "valid":
            reasons.append(f"artifact_not_validated:{artifact.filename}")
    if contract.require_primary_artifact and not ws.artifacts:
        reasons.append("artifact_registry_empty")
    return reasons
