"""Runtime guards for Data Agent deliverables and anti-hallucination filters.

Domain grain column/role lists come from ``data_dictionary/analysis_grain.yaml``
via ``load_analysis_grain`` — do not bake retail column recipes here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from project_core.domain.analysis.ops.working_set import DatasetWorkingSet
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.schema.analysis_grain import load_analysis_grain

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


def _cols_upper(df: pd.DataFrame) -> set[str]:
    return {str(c).upper() for c in df.columns}


def dataset_looks_like_product_catalog(
    df: pd.DataFrame,
    *,
    role: str | None = None,
) -> bool:
    """Catalog-like: working-set role, else grain yaml (product ids without bill ids)."""
    grain = load_analysis_grain()
    if (role or "").strip().lower() in set(grain.catalog_roles):
        return True
    cols = _cols_upper(df)
    has_product = bool(cols & set(grain.product_id_columns))
    has_bill = bool(cols & set(grain.bill_id_columns))
    return has_product and not has_bill


def frame_has_bill_grain(df: pd.DataFrame) -> bool:
    grain = load_analysis_grain()
    return bool(_cols_upper(df) & set(grain.bill_id_columns))


def is_blocked_name_type_guess(
    *,
    product_codes: list[str],
    op_id: str,
    args: dict[str, Any],
) -> str | None:
    """Meta policy: with product_codes, do not select SKUs via display-name filters."""
    if not product_codes or op_id != "filter_rows":
        return None
    display_cols = set(load_analysis_grain().display_name_columns)
    for clause in _clause_list(args):
        col = str(clause.get("column") or clause.get("column_name") or "").strip().upper()
        if col not in display_cols:
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
    """Block exporting catalog/aggregate frames when the brief still needs bill deliverables."""
    needs_bills = checklist.get("top_n") is not None or checklist.get("min_bill_value") is not None
    if not needs_bills:
        return None
    ref = str(dataset or "").strip()
    if not ref or not working_set.has(ref):
        return None
    grain = load_analysis_grain()
    ref_l = ref.lower()
    handle = working_set.get(ref)
    role = getattr(handle, "role", None)
    if any(h in ref_l for h in grain.catalog_ref_substrings) or dataset_looks_like_product_catalog(
        handle.frame(), role=str(role) if role else None
    ):
        return "blocked_export_product_catalog_before_bills"
    # Prefer bill-grained frames when one exists; block pure aggregates.
    if not frame_has_bill_grain(handle.frame()) and prefer_export_dataset_ref(
        working_set, needs_bill=True
    ) not in {None, ref}:
        return "blocked_export_non_bill_when_bills_available"
    return None


def _partition_key_column(df: pd.DataFrame) -> str | None:
    cols = set(df.columns)
    for col in ("SKU_ID", "SKU_CODE"):
        if col in cols:
            return col
    return None


def resolved_sku_ids_from_working_set(
    working_set: DatasetWorkingSet,
    product_codes: list[str] | None = None,
) -> list[str]:
    """SKU_IDs from resolve_products (preferred) or frames matching brief codes."""
    codes = [str(c).strip() for c in (product_codes or []) if str(c).strip()]
    for ref in working_set.refs():
        if "resolv" not in str(ref).lower():
            continue
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if "SKU_ID" not in df.columns:
            continue
        ids = [str(x).strip() for x in df["SKU_ID"].tolist() if str(x).strip()]
        if ids:
            return list(dict.fromkeys(ids))
    if not codes:
        return []
    matched: list[str] = []
    for ref in working_set.refs():
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if "SKU_ID" not in df.columns:
            continue
        series = df["SKU_ID"].astype(str)
        for sku in series.unique().tolist():
            s = str(sku)
            if any(c in s for c in codes):
                matched.append(s)
    return list(dict.fromkeys(matched))


def filter_frame_to_product_scope(
    df: pd.DataFrame,
    *,
    sku_ids: list[str] | None = None,
    product_codes: list[str] | None = None,
) -> pd.DataFrame:
    """Keep rows for resolved SKU_IDs / brief product codes when a product column exists."""
    ids = [str(x).strip() for x in (sku_ids or []) if str(x).strip()]
    codes = [str(c).strip() for c in (product_codes or []) if str(c).strip()]
    if not ids and not codes:
        return df
    part = _partition_key_column(df)
    if part is None:
        return df
    series = df[part].astype(str)
    if ids:
        return df.loc[series.isin(ids)].copy()
    mask = False
    for c in codes:
        mask = mask | series.str.contains(re.escape(c), regex=True, na=False)
    return df.loc[mask].copy() if isinstance(mask, pd.Series) else df


def is_partitioned_top_n_ref(working_set: DatasetWorkingSet, ref: str | None) -> bool:
    """True when ref is already a per-group top-N deliverable (do not globally re-limit)."""
    if not ref or not working_set.has(ref):
        return False
    handle = working_set.get(ref)
    source = str((handle.meta or {}).get("source") or "")
    if source == "top_n_per_group":
        return True
    lineage = getattr(working_set, "lineage", None) or {}
    node = lineage.get(ref) if isinstance(lineage, dict) else None
    if node is not None and str(getattr(node, "op_id", "") or "") == "top_n_per_group":
        return True
    ref_l = str(ref).lower()
    return any(tok in ref_l for tok in ("_per_", "per_group", "per_product", "ranked_"))


def prefer_export_dataset_ref(
    working_set: DatasetWorkingSet,
    *,
    needs_bill: bool,
    product_codes: list[str] | None = None,
) -> str | None:
    """Pick an export ref by grain/shape only — never force a domain SQL recipe."""
    scope_ids = resolved_sku_ids_from_working_set(working_set, product_codes)
    ranked: list[tuple[int, str]] = []
    for ref in working_set.refs():
        try:
            handle = working_set.get(ref)
            df = handle.frame()
        except Exception:  # noqa: BLE001
            continue
        n = len(df)
        # Empty frames must never win over populated ones (auto-repair trap).
        if n == 0:
            continue
        role = str(getattr(handle, "role", None) or "")
        if needs_bill and dataset_looks_like_product_catalog(df, role=role):
            continue
        score = 0
        cols_u = {str(c).upper() for c in df.columns}
        if needs_bill and frame_has_bill_grain(df):
            score += 100
            # Prefer line/join grain (bill id + product id) over header-only.
            if cols_u & {"SKU_ID", "SKU_CODE"}:
                score += 40
        # Prefer an already-ranked per-group top-N over raw joins / global slices.
        if is_partitioned_top_n_ref(working_set, ref):
            score += 80
        # Prefer frames scoped to brief product codes (avoid exporting all SKUs).
        if scope_ids and "SKU_ID" in df.columns:
            present = set(df["SKU_ID"].astype(str)) & set(scope_ids)
            extras = set(df["SKU_ID"].astype(str)) - set(scope_ids)
            if present:
                score += 60
            if extras and len(extras) > max(3, len(scope_ids) * 2):
                score -= 100
            elif present and not extras:
                score += 40
        # Prefer smaller analytical frames over huge probes.
        score += max(0, 50 - min(n, 50))
        ranked.append((score, ref))
    if not ranked:
        return None
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked[0][1]


def rank_bill_frame_for_export(
    working_set: DatasetWorkingSet,
    *,
    source_ref: str,
    top_n: int,
    out_dir: str | Path,
    save_as: str = "bills_top_n",
    partition_by: list[str] | None = None,
    product_codes: list[str] | None = None,
    sku_ids: list[str] | None = None,
) -> str:
    """Prepare a bill deliverable for export.

    - If ``source_ref`` is already ``top_n_per_group``, keep all rows (copy to save_as).
    - If ``partition_by`` is set (or multi-SKU frame + partition_by inferred by caller),
      run per-group top-N — never collapse to a global ``limit_rows(top_n)``.
    - Otherwise sort newest-first and apply a **global** top_n limit.
    """
    from project_core.domain.analysis.ops import execute_op

    out = Path(out_dir)
    scope_ids = list(sku_ids or []) or resolved_sku_ids_from_working_set(
        working_set, product_codes
    )
    active_ref = source_ref
    try:
        src_df = working_set.get(source_ref).frame()
    except Exception:  # noqa: BLE001
        src_df = None
    if src_df is not None and (scope_ids or product_codes):
        scoped = filter_frame_to_product_scope(
            src_df, sku_ids=scope_ids, product_codes=product_codes
        )
        if len(scoped) == 0:
            # Keep source — coverage will flag product_codes_missing.
            pass
        elif len(scoped) < len(src_df):
            scoped_as = f"{save_as}_scoped"
            handle = working_set.get(source_ref)
            working_set.save_frame(
                scoped_as,
                scoped,
                role=getattr(handle, "role", None) or "fact",
                source="product_scope_filter",
                parents=[source_ref],
            )
            active_ref = scoped_as

    if is_partitioned_top_n_ref(working_set, active_ref):
        if active_ref == save_as:
            return active_ref
        df_ready = working_set.get(active_ref).frame().copy()
        handle = working_set.get(active_ref)
        working_set.save_frame(
            save_as,
            df_ready,
            role=getattr(handle, "role", None) or "fact",
            source="top_n_per_group",
            op_id="top_n_per_group",
            parents=[active_ref],
        )
        return save_as

    df = working_set.get(active_ref).frame()
    parts = [str(c) for c in (partition_by or []) if str(c) in df.columns]
    order_cols = [
        c
        for c in (
            "TRAN_DATE",
            "TRAN_DATE_y",
            "TRAN_DATE_x",
            "TRAN_DATE_hdr",
            "TRAN_DATE_line",
            "TRAN_TIME",
            "TRAN_TIME_y",
            "TRAN_TIME_x",
            "TRAN_TIME_hdr",
            "TRAN_TIME_line",
        )
        if c in df.columns
    ]
    if parts:
        result = execute_op(
            working_set,
            "top_n_per_group",
            {
                "dataset": active_ref,
                "partition_by": parts,
                "order_by": order_cols or list(df.columns[:1]),
                "n": max(1, int(top_n)),
                "ascending": False,
                "save_as": save_as,
            },
            out_dir=out,
        )
        if result.status == "ok":
            return save_as
        return active_ref

    ranked_ref = active_ref
    if order_cols:
        sorted_as = f"{save_as}_sorted"
        result = execute_op(
            working_set,
            "sort_rows",
            {
                "dataset": active_ref,
                "by": order_cols,
                "ascending": [False] * len(order_cols),
                "save_as": sorted_as,
            },
            out_dir=out,
        )
        if result.status == "ok":
            ranked_ref = sorted_as
    limited = execute_op(
        working_set,
        "limit_rows",
        {"dataset": ranked_ref, "n": max(1, int(top_n)), "save_as": save_as},
        out_dir=out,
    )
    if limited.status == "ok":
        return save_as
    return ranked_ref


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

    grain = load_analysis_grain()
    best: tuple[int, str, pd.DataFrame] | None = None
    for ref in working_set.refs():
        if ref.startswith("fetch_") or ref in {"resolved_skus", "resolved_sku", "resolved_product"}:
            continue
        try:
            handle = working_set.get(ref)
            df = handle.frame()
        except Exception:  # noqa: BLE001
            continue
        cols = _cols_upper(df)
        role = str(getattr(handle, "role", None) or "")
        # Prefer bill-grained frames over catalogs / huge probes.
        score = len(df)
        if cols & set(grain.bill_id_columns):
            score -= 500_000
        if dataset_looks_like_product_catalog(df, role=role):
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
    """Structural deliverable checks (readable, top-N, catalog-vs-bills).

    Does **not** require product-id columns on the export sheet when the brief
    mentions product codes / quantity metrics — that was domain hardcoding.
    Product filtering is enforced upstream via fetch sugar / working set.

    When the deliverable is per-group top-N (or multi-SKU bill grain), ``top_n``
    is checked as max rows **per partition**, not as a global row cap.
    """
    n_limit = top_n if top_n is not None else infer_top_n(brief)

    df, source = primary_deliverable_frame(working_set)
    gaps: list[str] = []
    caveats: list[str] = []
    row_count = int(len(df)) if df is not None else None
    columns = [str(c) for c in df.columns] if df is not None else []
    is_bill_frame = bool(df is not None and frame_has_bill_grain(df))

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

    if n_limit is not None:
        if not is_bill_frame:
            gaps.append("missing_bill_evidence_columns")
        if dataset_looks_like_product_catalog(df):
            gaps.append("catalog_export_without_bills")

        part_col = _partition_key_column(df) if df is not None else None
        partitioned = False
        if source and not str(source).lower().endswith((".xlsx", ".xls", ".xlsm")):
            partitioned = is_partitioned_top_n_ref(working_set, str(source))
        codes = [str(c).strip() for c in (product_codes or []) if str(c).strip()]
        if not partitioned and part_col and len(codes) > 1:
            partitioned = True
        if not partitioned and part_col and row_count is not None and row_count > n_limit:
            max_per = int(df.groupby(df[part_col].astype(str)).size().max())
            if max_per <= n_limit:
                partitioned = True

        if partitioned and part_col is not None and df is not None:
            max_per = int(df.groupby(df[part_col].astype(str)).size().max())
            if max_per > n_limit:
                gaps.append(f"top_n_mismatch:got_{max_per}_per_group_want_<={n_limit}")
            elif row_count is not None and row_count < n_limit:
                caveats.append(f"fewer_than_requested:got_{row_count}_want_{n_limit}")
        else:
            if row_count is not None and row_count > n_limit:
                gaps.append(f"top_n_mismatch:got_{row_count}_want_<={n_limit}")
            elif row_count is not None and row_count < n_limit:
                caveats.append(f"fewer_than_requested:got_{row_count}_want_{n_limit}")

        # Brief product codes must constrain the deliverable — not every SKU in a join.
        if codes and df is not None and part_col is not None:
            scope_ids = resolved_sku_ids_from_working_set(working_set, codes)
            series = df[part_col].astype(str)
            unique_n = int(series.nunique())
            if scope_ids:
                present = set(series) & set(scope_ids)
                extras = set(series) - set(scope_ids)
                if not present:
                    gaps.append("product_codes_missing_from_deliverable")
                elif len(extras) > max(3, len(scope_ids) * 2):
                    gaps.append(f"product_scope_extra_skus:{len(extras)}")
            elif unique_n > max(len(codes) * 3, 10):
                gaps.append(f"product_scope_mismatch:got_{unique_n}_skus_want_~{len(codes)}")

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
        or g.startswith("product_scope_")
        or g
        in {
            "missing_bill_evidence_columns",
            "deliverable_unreadable",
            "catalog_export_without_bills",
            "product_codes_missing_from_deliverable",
            "resolve_products_empty",
        }
        for g in gaps
    )


def is_nonblocking_type_clarify(
    *,
    product_codes: list[str],
    thought: str = "",
    decision: dict[str, Any] | None = None,
    product_type_soft: str | None = None,
    resolved_sku_count: int | None = None,
) -> bool:
    """Meta: clarify about soft type / display-name while codes already pin SKUs.

    Hard blockers (missing identity/time/store) are NOT non-blocking — those still
    clarify. Soft descriptive filters (ITEM_TYPE empty, gift/KM labels, FULL_NAME)
    must not stop the run when product_codes already select SKUs.

    ``resolved_sku_count``: when a resolve_products attempt already returned 0 rows,
    codes do **not** pin SKUs — always escalate. Display-name-looking "codes"
    (spaces / non-ASCII) also do not count as pinned identity.
    """
    if not product_codes:
        return False
    # Failed resolve → user must confirm name/code; do not swallow.
    if resolved_sku_count is not None and int(resolved_sku_count) <= 0:
        return False
    # Spoken product names in brief.filters.product_code are not SKU pins.
    if any(
        (" " in str(c).strip()) or any(ord(ch) > 127 for ch in str(c))
        for c in product_codes
        if str(c).strip()
    ):
        return False
    blob = " ".join(
        [
            str(thought or ""),
            json.dumps(decision or {}, ensure_ascii=False, default=str),
        ]
    ).lower()
    # True blockers — do not swallow.
    hard = (
        "time_range",
        "missing time",
        "thiếu ngày",
        "thieu ngay",
        "which store",
        "cửa hàng nào",
        "cua hang nao",
        "missing sku",
        "unknown product",
        "không rõ mã",
        "khong ro ma",
        "0 rows",
        "zero rows",
        "not found",
        "không tìm thấy",
        "khong tim thay",
        "no product",
        "resolve_products",
    )
    if any(tok in blob for tok in hard):
        return False
    soft = str(product_type_soft or "").strip().lower()
    if soft and soft in blob:
        return True
    markers = (
        "product_type",
        "product type",
        "product_type_soft",
        "item_type",
        "item type",
        "sparse_column",
        "sparse_column_unusable",
        "full_name",
        "full name",
        "display name",
        "product name",
        "tên hàng",
        "ten hang",
        "loại hàng",
        "loai hang",
        "quà tặng",
        "qua tang",
        "gift",
        " soft filter",
        "soft/descriptive",
        # Already-provided codes: do not ask user to reconfirm / remap column.
        "product codes are correct",
        "provided product codes",
        "mapped to a different column",
        "alternative way to identify",
        "alternative identification",
        "mã barcode",
        "ma barcode",
        "barcode/sku",
        "sku khác",
        "sku khac",
        "xác nhận chúng là mã",
        "xac nhan chung la ma",
        "do not exist in the `sku_id`",
        "do not exist in the sku_id",
        "không tồn tại trong sku_id",
        "khong ton tai trong sku_id",
        # Join suffix collisions (AMOUNT → AMOUNT_x / AMOUNT_hdr) are ops issues,
        # not user questions — prefer header/bill total when codes + min_bill exist.
        "amount_x",
        "amount_y",
        "amount_hdr",
        "amount_line",
        "header amount",
        "line item",
        "line amount",
        "tổng giá trị của hóa đơn",
        "tong gia tri cua hoa don",
        "từng dòng sản phẩm",
        "tung dong san pham",
        "which 'amount'",
        "which amount",
        "missing_columns:[amount]",
        "column name collisions",
        "duplicate column names",
    )
    if any(tok in blob for tok in markers):
        return True
    # Codes pin SKUs — "is this a gift/KM type?" debates are non-blocking.
    if any(tok in blob for tok in ("km", "gift", "quà", "qua ")) and any(
        tok in blob for tok in ("type", "loại", "loai", "filter", "lọc", "loc", "identify")
    ):
        return True
    return False
