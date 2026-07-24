"""Runtime guards for Data Agent deliverables and anti-hallucination filters."""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd

from project_core.domain.analysis.ops.working_set import DatasetWorkingSet
from project_core.domain.contracts.brief import AnalysisBrief

_NAME_TYPE_COLUMNS = {
    "FULL_NAME",
    "SKU_NAME",
    "PRODUCT_NAME",
    "TEN_HANG",
    "NAME",
    "ITEM_NAME",
    "DESCRIPTION",
}

_TOP_N_FILTER_KEYS = (
    "top_n",
    "limit",
    "n",
    "top",
    "bill_limit",
    "max_bills",
    "n_bills",
    "top_bills",
)


def soft_product_type(brief: AnalysisBrief) -> str | None:
    """Optional product_type hint — never a hard filter when product codes exist."""
    raw = (brief.filters or {}).get("product_type")
    if raw is None:
        raw = (brief.filters or {}).get("product_form")
    text = str(raw or "").strip()
    return text or None


def infer_top_n(brief: AnalysisBrief) -> int | None:
    """Extract top-N from filters, ranking requirements, or light intent parse."""
    filters = brief.filters or {}
    for key in _TOP_N_FILTER_KEYS:
        if filters.get(key) is None:
            continue
        try:
            n = int(filters[key])
        except (TypeError, ValueError):
            continue
        if n > 0:
            return n

    for req in brief.requirements or []:
        if getattr(req, "kind", None) != "ranking":
            continue
        value = getattr(req, "value", None)
        if isinstance(value, dict):
            for key in ("n", "top_n", "limit", "k"):
                if value.get(key) is None:
                    continue
                try:
                    n = int(value[key])
                except (TypeError, ValueError):
                    continue
                if n > 0:
                    return n
        elif isinstance(value, (int, float)) and int(value) > 0:
            return int(value)
        key = str(getattr(req, "key", "") or "")
        match = re.search(r"(\d+)", key)
        if match:
            n = int(match.group(1))
            if n > 0:
                return n

    blob = " ".join(
        [
            str(brief.intent or ""),
            " ".join(str(x) for x in (brief.metrics or [])),
            " ".join(f"{k}={v}" for k, v in filters.items()),
        ]
    )
    patterns = (
        r"(?:top|lấy|lay)\s*(\d+)\s*(?:bill|hóa\s*đơn|hoa\s*don|hđ|hd)\b",
        r"(\d+)\s*(?:bill|hóa\s*đơn|hoa\s*don)\s*(?:gần\s*nhất|gan\s*nhat|mới\s*nhất|moi\s*nhat)\b",
        r"\btop[\s_-]*(\d+)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, blob, flags=re.IGNORECASE)
        if match:
            n = int(match.group(1))
            if 0 < n <= 1000:
                return n
    return None


def _clause_list(args: dict[str, Any]) -> list[dict[str, Any]]:
    raw = args.get("clauses") or args.get("conditions") or args.get("filters")
    if isinstance(raw, list):
        return [c for c in raw if isinstance(c, dict)]
    if args.get("column") is not None or args.get("column_name") is not None:
        return [
            {
                "column": args.get("column") or args.get("column_name"),
                "op": args.get("op") or args.get("operator") or "eq",
                "value": args.get("value"),
            }
        ]
    return []


_BILL_ID_COLS = ("TRANS_NUM", "BILL_NO", "TRANS_ID")
_SKU_COLS = ("SKU_CODE", "SKU_ID")
_CATALOG_REF_HINTS = (
    "resolved_sku",
    "resolved_product",
    "products",
    "sku_def",
)


def dataset_looks_like_product_catalog(df: pd.DataFrame) -> bool:
    cols = {str(c).upper() for c in df.columns}
    has_sku = bool(cols & set(_SKU_COLS))
    has_bill = bool(cols & set(_BILL_ID_COLS))
    return has_sku and not has_bill


def is_blocked_name_type_guess(
    *,
    product_codes: list[str],
    op_id: str,
    args: dict[str, Any],
) -> str | None:
    """Meta policy: with product_codes, do not select SKUs via display-name filters."""
    if not product_codes or op_id != "filter_rows":
        return None
    for clause in _clause_list(args):
        col = str(clause.get("column") or clause.get("column_name") or "").strip().upper()
        if col not in _NAME_TYPE_COLUMNS:
            continue
        op = str(clause.get("op") or clause.get("operator") or "eq").strip().lower()
        if op in {"contains", "startswith", "endswith", "eq", "like", "regex", "ne"}:
            return "blocked_name_type_guess"
    return None


def is_blocked_premature_export(
    *,
    checklist: dict[str, Any],
    dataset: str | None,
    working_set: DatasetWorkingSet,
) -> str | None:
    """Block exporting SKU-catalog frames when the brief still needs bill deliverables."""
    needs_bills = checklist.get("top_n") is not None or checklist.get("min_bill_value") is not None
    if not needs_bills:
        return None
    ref = str(dataset or "").strip()
    if not ref or not working_set.has(ref):
        return None
    ref_l = ref.lower()
    if any(h in ref_l for h in _CATALOG_REF_HINTS) or dataset_looks_like_product_catalog(
        working_set.get(ref).frame()
    ):
        return "blocked_export_product_catalog_before_bills"
    return None


def primary_deliverable_frame(
    working_set: DatasetWorkingSet,
) -> tuple[pd.DataFrame | None, str | None]:
    """Prefer exported Excel (bills sheet if present); else best analysis dataset."""
    candidates: list[str] = []
    for path in list(getattr(working_set, "excel_artifacts", None) or []) + list(
        working_set.artifact_paths or []
    ):
        if str(path).lower().endswith((".xlsx", ".xls", ".xlsm")):
            candidates.append(str(path))
    for path in candidates:
        try:
            xl = pd.ExcelFile(path)
            sheet = "bills" if "bills" in xl.sheet_names else xl.sheet_names[0]
            return pd.read_excel(path, sheet_name=sheet), path
        except Exception:  # noqa: BLE001
            continue

    best: tuple[int, str, pd.DataFrame] | None = None
    for ref in working_set.refs():
        if ref.startswith("fetch_") or ref in {"resolved_skus", "resolved_sku", "resolved_product"}:
            continue
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        cols = {str(c).upper() for c in df.columns}
        # Prefer bill-grained frames over catalogs / huge probes.
        score = len(df)
        if cols & set(_BILL_ID_COLS):
            score -= 500_000
        if dataset_looks_like_product_catalog(df):
            score += 500_000
        if best is None or score < best[0]:
            best = (score, ref, df)
    if best is None:
        return None, None
    return best[2], best[1]


def assess_deliverable_coverage(
    brief: AnalysisBrief,
    working_set: DatasetWorkingSet,
    *,
    product_codes: list[str] | None = None,
    top_n: int | None = None,
) -> dict[str, Any]:
    """Check Excel/table against brief obligations (SKU evidence + top-N)."""
    codes = list(product_codes if product_codes is not None else [])
    if not codes:
        raw = (brief.filters or {}).get("product_code")
        if isinstance(raw, list):
            codes = [str(x).strip() for x in raw if str(x).strip()]
        elif raw is not None and str(raw).strip():
            codes = [str(raw).strip()]
    n_limit = top_n if top_n is not None else infer_top_n(brief)

    df, source = primary_deliverable_frame(working_set)
    gaps: list[str] = []
    caveats: list[str] = []
    row_count = int(len(df)) if df is not None else None
    columns = [str(c) for c in df.columns] if df is not None else []
    cols_u = {c.upper() for c in columns}
    is_bill_frame = bool(set(_BILL_ID_COLS) & cols_u)

    if df is None or row_count is None:
        if working_set.artifact_paths or working_set.refs():
            gaps.append("deliverable_unreadable")
        return {
            "ok": False,
            "gaps": gaps,
            "caveats": caveats,
            "row_count": row_count,
            "columns": columns,
            "source": source,
            "top_n": n_limit,
        }

    if codes and not ({"SKU_CODE", "SKU_ID"} & cols_u):
        # Bill sheet may omit SKU when quantity is not requested.
        # If codes + quantity/revenue metrics are present, keep requiring SKU evidence.
        metrics = {str(m).lower() for m in (brief.metrics or [])}
        needs_sku_metrics = bool(metrics & {"quantity", "qty", "revenue", "amount", "sales"})
        if not (n_limit is not None and is_bill_frame and not needs_sku_metrics):
            gaps.append("missing_sku_evidence_columns")

    if n_limit is not None:
        if not is_bill_frame:
            gaps.append("missing_bill_evidence_columns")
        if dataset_looks_like_product_catalog(df):
            gaps.append("catalog_export_without_bills")
        if row_count > n_limit:
            gaps.append(f"top_n_mismatch:got_{row_count}_want_<={n_limit}")
        elif row_count < n_limit:
            caveats.append(
                f"fewer_than_requested:got_{row_count}_want_{n_limit}"
            )

    return {
        "ok": not gaps,
        "gaps": gaps,
        "caveats": caveats,
        "row_count": row_count,
        "columns": columns,
        "source": source,
        "top_n": n_limit,
    }


def coverage_forces_partial(gaps: list[str]) -> bool:
    return any(
        g.startswith("top_n_mismatch")
        or g
        in {
            "missing_sku_evidence_columns",
            "missing_bill_evidence_columns",
            "deliverable_unreadable",
            "catalog_export_without_bills",
        }
        for g in gaps
    )


def is_nonblocking_type_clarify(
    *,
    product_codes: list[str],
    thought: str = "",
    decision: dict[str, Any] | None = None,
    product_type_soft: str | None = None,
) -> bool:
    """Meta: clarify about soft type / display-name while codes already pin SKUs."""
    if not product_codes:
        return False
    blob = " ".join(
        [
            str(thought or ""),
            json.dumps(decision or {}, ensure_ascii=False, default=str),
        ]
    ).lower()
    soft = str(product_type_soft or "").strip().lower()
    if soft and soft in blob:
        return True
    markers = (
        "product_type",
        "product type",
        "full_name",
        "full name",
        "display name",
        "product name",
        "product_type_soft",
    )
    return any(tok in blob for tok in markers)
