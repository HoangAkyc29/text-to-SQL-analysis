"""Deterministic binding and preflight for version-2 catalog recipes."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Mapping

from project_core.domain.analysis.ops.registry import (
    OP_SPECS,
    list_op_ids,
    missing_required_args,
    normalize_op_args,
)
from project_core.domain.contracts.analysis_plan import RecipeDatasetContract


_TEMPLATE = re.compile(r"^\{\{(dataset|param|output)\.([A-Za-z0-9_.-]+)\}\}$")
_DATASET_ARG_KEYS = {"dataset", "left", "right"}


@dataclass
class RecipePreflight:
    compatible: bool
    op_chain: list[dict[str, Any]] = field(default_factory=list)
    dataset_bindings: dict[str, str] = field(default_factory=dict)
    rejection_reasons: list[str] = field(default_factory=list)


def is_recipe_v2(tool: Mapping[str, Any]) -> bool:
    return (
        tool.get("kind") == "catalog_op_chain"
        and int(tool.get("compatibility_version") or 0) == 2
        and isinstance(tool.get("op_chain"), list)
        and bool(tool.get("op_chain"))
        and not tool.get("script_template")
    )


def canonicalize_op_chain(steps: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Keep executable catalog instructions and normalize aliases."""
    chain: list[dict[str, Any]] = []
    for raw in steps or []:
        if not isinstance(raw, dict) or not raw.get("op_id"):
            continue
        if raw.get("status") is not None and not any(
            key in raw for key in ("args", "dataset", "save_as")
        ):
            continue
        op_id = str(raw["op_id"])
        args = dict(raw.get("args") or {})
        if raw.get("dataset") is not None:
            args.setdefault("dataset", raw["dataset"])
        if raw.get("save_as") is not None:
            args.setdefault("save_as", raw["save_as"])
        args, _ = normalize_op_args(op_id, args)
        step: dict[str, Any] = {"op_id": op_id, "args": args}
        if raw.get("output") is not None:
            step["output"] = str(raw["output"])
        chain.append(step)
    return chain


def bind_and_preflight(
    tool: Mapping[str, Any],
    datasets: list[Mapping[str, Any]],
    *,
    params: Mapping[str, Any] | None = None,
    available_ops: set[str] | None = None,
) -> RecipePreflight:
    reasons: list[str] = []
    if not is_recipe_v2(tool):
        return RecipePreflight(False, rejection_reasons=["recipe_not_canonical_v2"])

    available = set(available_ops) if available_ops is not None else set(list_op_ids())
    contracts = _dataset_contracts(tool, reasons)
    bindings = _bind_roles(contracts, datasets, reasons)
    known_refs = set(bindings.values())
    known_outputs: set[str] = set()
    bound_chain: list[dict[str, Any]] = []

    for index, step in enumerate(canonicalize_op_chain(tool.get("op_chain"))):
        op_id = step["op_id"]
        prefix = f"step[{index}]:{op_id}"
        if op_id not in available or op_id not in OP_SPECS:
            reasons.append(f"{prefix}:op_unavailable")
            continue
        _check_output_refs(step["args"], known_outputs, prefix, reasons)
        args = _resolve_value(
            step["args"],
            datasets=bindings,
            params=dict(params or {}),
            outputs={},
            reasons=reasons,
            location=prefix,
            allow_output=True,
        )
        missing = missing_required_args(op_id, args)
        if missing:
            reasons.append(f"{prefix}:missing_required_args:{','.join(missing)}")
        _check_dataset_refs(prefix, args, known_refs, reasons)
        save_as = args.get("save_as")
        if save_as:
            known_refs.add(str(save_as))
        known_outputs.add(str(step.get("output") or f"step{index}"))
        bound_chain.append({"op_id": op_id, "args": args, **(
            {"output": step["output"]} if step.get("output") else {}
        )})

    return RecipePreflight(
        compatible=not reasons,
        op_chain=bound_chain,
        dataset_bindings=bindings,
        rejection_reasons=list(dict.fromkeys(reasons)),
    )


def resolve_runtime_args(
    args: Mapping[str, Any],
    *,
    dataset_bindings: Mapping[str, str],
    params: Mapping[str, Any],
    outputs: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    resolved = _resolve_value(
        dict(args),
        datasets=dataset_bindings,
        params=params,
        outputs=outputs,
        reasons=reasons,
        location="runtime",
        allow_output=False,
    )
    if reasons:
        raise ValueError(";".join(reasons))
    return resolved


def _dataset_contracts(
    tool: Mapping[str, Any], reasons: list[str]
) -> list[RecipeDatasetContract]:
    contracts: list[RecipeDatasetContract] = []
    for raw in tool.get("dataset_contracts") or []:
        try:
            contracts.append(RecipeDatasetContract.model_validate(raw))
        except Exception:
            reasons.append("invalid_dataset_contract")
    if not contracts:
        reasons.append("dataset_contracts_required")
    roles = [c.role for c in contracts]
    if len(roles) != len(set(roles)):
        reasons.append("duplicate_dataset_role")
    return contracts


def _bind_roles(
    contracts: list[RecipeDatasetContract],
    datasets: list[Mapping[str, Any]],
    reasons: list[str],
) -> dict[str, str]:
    bindings: dict[str, str] = {}
    used: set[str] = set()
    for contract in contracts:
        matches = [
            ds for ds in datasets
            if str(ds.get("role") or "") == contract.role
            and str(ds.get("ref") or "") not in used
        ]
        if not matches and len(contracts) == 1 and len(datasets) == 1:
            matches = [datasets[0]]
        compatible: list[Mapping[str, Any]] = []
        for ds in matches:
            columns = {str(c) for c in ds.get("columns") or []}
            if set(contract.required_columns).issubset(columns):
                if contract.source_kind and ds.get("source_kind") not in {
                    None, contract.source_kind
                }:
                    continue
                actual_dtypes = {
                    str(key): str(value).lower()
                    for key, value in (ds.get("dtypes") or {}).items()
                }
                if any(
                    column in actual_dtypes
                    and str(expected).lower() != actual_dtypes[column]
                    for column, expected in contract.dtypes.items()
                ):
                    continue
                compatible.append(ds)
        if not compatible:
            reasons.append(f"dataset_role_unbound:{contract.role}")
            continue
        if len(compatible) > 1:
            reasons.append(f"dataset_role_ambiguous:{contract.role}")
            continue
        chosen = compatible[0]
        ref = str(chosen.get("ref") or "")
        if not ref:
            reasons.append(f"dataset_ref_missing:{contract.role}")
            continue
        bindings[contract.role] = ref
        used.add(ref)
    return bindings


def _resolve_value(
    value: Any,
    *,
    datasets: Mapping[str, str],
    params: Mapping[str, Any],
    outputs: Mapping[str, Any],
    reasons: list[str],
    location: str,
    allow_output: bool,
) -> Any:
    if isinstance(value, dict):
        return {
            key: _resolve_value(
                item,
                datasets=datasets,
                params=params,
                outputs=outputs,
                reasons=reasons,
                location=f"{location}.{key}",
                allow_output=allow_output,
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            _resolve_value(
                item,
                datasets=datasets,
                params=params,
                outputs=outputs,
                reasons=reasons,
                location=location,
                allow_output=allow_output,
            )
            for item in value
        ]
    if not isinstance(value, str):
        return value
    match = _TEMPLATE.match(value)
    if not match:
        if "{{" in value or "}}" in value:
            reasons.append(f"{location}:invalid_template")
        return value
    namespace, key = match.groups()
    source: Mapping[str, Any] = {
        "dataset": datasets,
        "param": params,
        "output": outputs,
    }[namespace]
    if key in source:
        return source[key]
    if namespace == "output" and allow_output:
        return value
    reasons.append(f"{location}:unbound_{namespace}:{key}")
    return value


def _check_dataset_refs(
    prefix: str,
    args: Mapping[str, Any],
    known_refs: set[str],
    reasons: list[str],
) -> None:
    for key in _DATASET_ARG_KEYS:
        value = args.get(key)
        if isinstance(value, str) and not value.startswith("{{") and value not in known_refs:
            reasons.append(f"{prefix}:unknown_dataset_ref:{value}")
    for value in args.get("datasets") or []:
        if str(value) not in known_refs:
            reasons.append(f"{prefix}:unknown_dataset_ref:{value}")
    for value in (args.get("sheets") or {}).values():
        if str(value) not in known_refs:
            reasons.append(f"{prefix}:unknown_dataset_ref:{value}")


def _check_output_refs(
    value: Any,
    known_outputs: set[str],
    prefix: str,
    reasons: list[str],
) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _check_output_refs(item, known_outputs, prefix, reasons)
        return
    if isinstance(value, list):
        for item in value:
            _check_output_refs(item, known_outputs, prefix, reasons)
        return
    if not isinstance(value, str):
        return
    match = _TEMPLATE.match(value)
    if not match or match.group(1) != "output":
        return
    output_name = match.group(2).split(".", 1)[0]
    if output_name not in known_outputs:
        reasons.append(f"{prefix}:unknown_output_ref:{output_name}")
