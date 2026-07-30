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


def as_str_list(value: Any) -> list[str]:
    """Normalize LLM caveats (string vs list) — never treat a string as char list."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        # list("some string") → single-char items; rejoin those.
        if value and all(isinstance(x, str) and len(x) <= 1 for x in value):
            rejoined = "".join(value).strip()
            return [rejoined] if rejoined else []
        out: list[str] = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                out.append(text)
        return out
    text = str(value).strip()
    return [text] if text else []


def _brief_deliverable_items(brief: AnalysisBrief) -> list[Any]:
    """Optional deliverable hints on brief-like objects (AnalysisBrief has no deliverables field)."""
    raw = getattr(brief, "deliverables", None)
    if not raw:
        return []
    return list(raw)


def ranking_targets_bills(brief: AnalysisBrief) -> bool:
    """True when top-N / ranking refers to bills/transactions, not SKU/store aggregates."""
    blob = " ".join(
        [
            str(brief.intent or ""),
            " ".join(str(m) for m in (brief.metrics or [])),
            " ".join(str(d) for d in (brief.dimensions or [])),
        ]
    ).lower()
    bill_tokens = ("bill", "hóa đơn", "hoa don", "hđ", "trans_num", "transaction")
    product_tokens = (
        "mặt hàng",
        "mat hang",
        "sku",
        "sản phẩm",
        "san pham",
        "product",
        "item",
        "doanh thu",
        "revenue",
    )
    has_bill = any(tok in blob for tok in bill_tokens)
    has_product = any(tok in blob for tok in product_tokens)
    if has_bill and not has_product:
        return True
    if has_product and not has_bill:
        return False
    for req in brief.requirements or []:
        if getattr(req, "kind", None) != "ranking":
            continue
        key = str(getattr(req, "key", "") or "").lower()
        if any(tok in key for tok in bill_tokens):
            return True
        if any(tok in key for tok in product_tokens):
            return False
    return False


def needs_bill_deliverable(brief: AnalysisBrief) -> bool:
    """True when the brief needs bill/line/customer grain (not catalog-only)."""
    if (brief.filters or {}).get("min_bill_value") is not None:
        return True
    if infer_top_n(brief) is not None and ranking_targets_bills(brief):
        return True
    grain = load_analysis_grain()
    dims = {str(d).strip().upper() for d in (brief.dimensions or []) if str(d).strip()}
    if dims & set(grain.bill_id_columns):
        return True
    if dims & set(grain.customer_id_columns):
        return True
    # Product filters alone do not imply bill grain — agent chooses the path.
    for item in _brief_deliverable_items(brief):
        if not isinstance(item, dict):
            text = str(item).lower()
        else:
            text = " ".join(
                str(item.get(k) or "")
                for k in ("kind", "type", "name", "label", "format", "grain")
            ).lower()
        if any(tok in text for tok in ("bill", "line", "trans", "customer", "card", "excel")):
            return True
    return False


def needs_customer_profile(brief: AnalysisBrief) -> bool:
    """True when the brief asks for customer/card profile fields (not walk-in lines only)."""
    grain = load_analysis_grain()
    dims = {str(d).strip().upper() for d in (brief.dimensions or []) if str(d).strip()}
    if dims & (set(grain.customer_id_columns) | set(grain.customer_profile_columns)):
        return True
    for item in _brief_deliverable_items(brief):
        if not isinstance(item, dict):
            text = str(item).lower()
        else:
            text = " ".join(
                str(item.get(k) or "")
                for k in ("kind", "type", "name", "label", "format", "grain")
            ).lower()
        if any(tok in text for tok in ("customer", "card", "phone", "profile", "khách")):
            return True
    return False


def looks_like_sku_code(value: Any) -> bool:
    """True for compact product codes — spoken names with spaces are not codes."""
    if value is None or isinstance(value, (bool, int, float, list, dict)):
        return False
    text = str(value).strip()
    if not text or " " in text:
        return False
    if len(text) > 64:
        return False
    return bool(re.match(r"^[A-Za-z0-9_\-./]+$", text))


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


def frame_has_customer_identity(df: pd.DataFrame) -> bool:
    grain = load_analysis_grain()
    return bool(_cols_upper(df) & set(grain.customer_id_columns))


def working_set_has_nonempty_bill_frame(working_set: DatasetWorkingSet) -> bool:
    for ref in working_set.refs():
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if len(df) > 0 and frame_has_bill_grain(df):
            return True
    return False


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
    """Block exporting catalog/aggregate frames when bill deliverables already exist."""
    needs_bills = (
        checklist.get("needs_bill")
        or checklist.get("min_bill_value") is not None
    )
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
    if re.search(r"(^|_)top[\d_\-]|^top_\d|ranked", ref_l):
        return True
    return any(tok in ref_l for tok in ("_per_", "per_group", "per_product", "ranked_"))


def prefer_export_dataset_ref(
    working_set: DatasetWorkingSet,
    *,
    needs_bill: bool,
    product_codes: list[str] | None = None,
) -> str | None:
    """Pick an export ref by grain/shape only — never force sheet/file recipes.

    ``needs_bill`` is the brief intent signal. Presence of bill-grained frames alone
    must not force bill export (product ranking briefs often still hold raw STRANS).
    """
    scope_ids = resolved_sku_ids_from_working_set(working_set, product_codes)
    prefer_bills = bool(needs_bill)
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
        # When the brief needs bill grain, never prefer product-catalog frames.
        if prefer_bills and dataset_looks_like_product_catalog(df, role=role):
            continue
        score = 0
        cols_u = {str(c).upper() for c in df.columns}
        grain = load_analysis_grain()
        if prefer_bills and frame_has_bill_grain(df):
            score += 100
            # Prefer line/join grain (bill id + product id) over header-only.
            if cols_u & set(grain.product_id_columns):
                score += 40
            if cols_u & set(grain.customer_id_columns):
                score += 30
            # Companion / expanded bill-line shapes beat product-only line slices.
            if cols_u & set(grain.customer_profile_columns):
                score += 25
        # Prefer an already-ranked / limited deliverable over raw probes.
        if is_partitioned_top_n_ref(working_set, ref):
            score += 80
        if not prefer_bills:
            if role == "aggregate":
                score += 55
            if is_partitioned_top_n_ref(working_set, ref):
                score += 40
            if n <= 50:
                score += 25
            if n >= 1000 and role == "fact":
                score -= 120
            # Raw bill-line facts are probes for aggregate briefs — demote them.
            if frame_has_bill_grain(df) and role == "fact" and n > 50:
                score -= 60
        # Prefer frames scoped to brief product codes (avoid exporting all SKUs).
        product_cols = [c for c in grain.product_id_columns if c in df.columns]
        if scope_ids and product_cols:
            part = product_cols[0]
            present = set(df[part].astype(str)) & set(scope_ids)
            extras = set(df[part].astype(str)) - set(scope_ids)
            if present:
                score += 60
            if prefer_bills:
                # Bill-detail briefs need companion lines on matching bills.
                if present and extras:
                    score += min(80, 30 + min(len(extras), 40))
                elif present and not extras:
                    # Product-only lines lose hard when an expanded companion exists.
                    score -= 40
                    if _working_set_has_expanded_companion(working_set, scope_ids):
                        score -= 80
            else:
                if extras and len(extras) > max(3, len(scope_ids) * 2):
                    score -= 100
                elif present and not extras:
                    score += 40
        # Prefer frames that already carry populated customer profile fields.
        profile_cols = [
            c
            for c in df.columns
            if str(c).upper() in set(grain.customer_profile_columns)
            or str(c).upper() in set(grain.customer_id_columns)
        ]
        populated_profile = 0
        for c in profile_cols:
            series = df[c].dropna().astype(str).str.strip()
            series = series[(series != "") & (series.str.lower() != "nan")]
            if len(series) > 0:
                populated_profile += 1
        if prefer_bills and populated_profile:
            score += min(45, populated_profile * 15)
        # Huge unscoped masters lose to focused analytical frames.
        if n >= 1000 and not (prefer_bills and frame_has_bill_grain(df)):
            score -= 80
        # Prefer smaller analytical frames over huge probes.
        score += max(0, 50 - min(n, 50))
        ranked.append((score, ref))
    if not ranked:
        return None
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked[0][1]


def _frame_has_populated_profile(df: pd.DataFrame) -> bool:
    grain = load_analysis_grain()
    for col in df.columns:
        cu = str(col).upper()
        if cu not in set(grain.customer_profile_columns):
            continue
        series = df[col].dropna().astype(str).str.strip()
        series = series[(series != "") & (series.str.lower() != "nan")]
        if len(series) > 0:
            return True
    return False


def _resolve_card_col(df: pd.DataFrame) -> str | None:
    upper = {str(c).upper(): str(c) for c in df.columns}
    for cand in ("CARD_ID", "CARD_ID_HDR", "CARD_ID_LINE", "CARD_ID_X", "CARD_ID_Y"):
        if cand in upper:
            return upper[cand]
    for u, c in upper.items():
        if u.startswith("CARD_ID"):
            return c
    return None


def ensure_bill_customer_join(
    working_set: DatasetWorkingSet,
    *,
    out_dir: str | Path,
    product_codes: list[str] | None = None,
    save_as: str = "bills_with_customer",
) -> str | None:
    """Join the best bill frame to a customer master on CARD_ID when profile is missing.

    Structural repair only — uses grain identity columns, not domain recipes.
    Prefers expanded companion bill-line frames over product-only joins that
    already happen to carry (partial) customer columns.
    """
    from project_core.domain.analysis.ops import execute_op

    scope_ids = resolved_sku_ids_from_working_set(working_set, product_codes)
    ranked: list[tuple[int, str]] = []
    for ref in working_set.refs():
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if df is None or len(df) == 0 or not frame_has_bill_grain(df):
            continue
        if dataset_looks_like_product_catalog(df):
            continue
        part = _partition_key_column(df)
        # Prefer line/companion frames; skip huge header-only dumps when product evidence exists.
        if part is None:
            if scope_ids or len(df) >= 1000:
                continue
            score = len(df)
        else:
            score = len(df)
            if scope_ids:
                series = df[part].astype(str)
                present = set(series) & set(scope_ids)
                extras = set(series) - set(scope_ids)
                if present:
                    score += 1000
                if extras:
                    score += 500 + min(len(extras), 100)
                elif present:
                    score -= 200
        ref_l = str(ref).lower()
        if "_all_bill_lines" in ref_l or "bill_lines" in ref_l:
            score += 200
        ranked.append((score, ref))
    if not ranked:
        return None
    ranked.sort(key=lambda x: (-x[0], x[1]))
    bill_ref = ranked[0][1]
    bill_df = working_set.get(bill_ref).frame()

    customer_ref: str | None = None
    customer_card: str | None = None
    for ref in working_set.refs():
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if df is None or len(df) == 0:
            continue
        if frame_has_bill_grain(df):
            continue
        if not _frame_has_populated_profile(df):
            continue
        card = _resolve_card_col(df)
        if not card:
            continue
        customer_ref = ref
        customer_card = card
        break

    if _frame_has_populated_profile(bill_df):
        # Still re-join if an expanded companion base is larger / has more SKUs.
        if customer_ref is None:
            return bill_ref
        part = _partition_key_column(bill_df)
        if part is None or not scope_ids:
            return bill_ref
        extras = set(bill_df[part].astype(str)) - set(scope_ids)
        if extras:
            return bill_ref

    left_card = _resolve_card_col(bill_df)
    if not left_card or not customer_ref or not customer_card:
        return bill_ref

    if working_set.has(save_as):
        try:
            existing = working_set.get(save_as).frame()
            if _frame_has_populated_profile(existing) and frame_has_bill_grain(existing):
                part = _partition_key_column(existing)
                if part is not None and scope_ids:
                    extras = set(existing[part].astype(str)) - set(scope_ids)
                    if extras:
                        return save_as
        except Exception:  # noqa: BLE001
            pass

    result = execute_op(
        working_set,
        "join_datasets",
        {
            "left": bill_ref,
            "right": customer_ref,
            "how": "left",
            "left_on": left_card,
            "right_on": customer_card,
            "save_as": save_as,
        },
        out_dir=Path(out_dir),
    )
    if getattr(result, "status", None) == "ok" and working_set.has(save_as):
        return save_as
    return bill_ref


def _resolve_col(df: pd.DataFrame, *candidates: str) -> str | None:
    cols = {str(c).upper(): str(c) for c in df.columns}
    for cand in candidates:
        if cand.upper() in cols:
            return cols[cand.upper()]
    # Suffix variants: STK_ID_hdr, CARD_ID_line, …
    for cand in candidates:
        cu = cand.upper()
        for col_u, col in cols.items():
            if col_u == cu or col_u.startswith(cu + "_"):
                return col
    return None


def _trim_export_columns(df: pd.DataFrame) -> pd.DataFrame:
    grain = load_analysis_grain()
    keep_roots = {c.upper() for c in grain.export_keep_columns}
    keep: list[str] = []
    for col in df.columns:
        cu = str(col).upper()
        for root_name in keep_roots:
            if cu == root_name or cu.startswith(root_name + "_"):
                keep.append(str(col))
                break
    if len(keep) < 3:
        return df
    return df.loc[:, keep].copy()


def _nonempty_mask(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    return series.notna() & (text != "") & (text.str.lower() != "nan") & (text.str.lower() != "none")


def prepare_bill_customer_export_sheets(
    working_set: DatasetWorkingSet,
    *,
    brief: AnalysisBrief,
    bill_ref: str,
    out_dir: str | Path,
) -> dict[str, str]:
    """Structural export prep: trim cols, map product names, split customers sheet.

    Does not hardcode store IDs or product names — uses grain roles + resolve frame.
    """
    from project_core.domain.analysis.ops import execute_op

    out = Path(out_dir)
    grain = load_analysis_grain()
    sheets: dict[str, str] = {}
    if not working_set.has(bill_ref):
        return sheets

    df = working_set.get(bill_ref).frame().copy()
    if needs_customer_profile(brief):
        card_col = _resolve_col(df, *grain.customer_id_columns[:1], "CARD_ID")
        if card_col:
            df = df.loc[_nonempty_mask(df[card_col])].copy()

    # Attach catalog display name from the richest SKU+name frame in the WS.
    name_cols = [c for c in grain.display_name_columns if _resolve_col(df, c)]
    sku_col = _resolve_col(df, *grain.product_id_columns)
    if sku_col and not name_cols:
        best_ref: str | None = None
        best_n = 0
        for ref in working_set.refs():
            try:
                rdf = working_set.get(ref).frame()
            except Exception:  # noqa: BLE001
                continue
            if rdf is None or len(rdf) == 0:
                continue
            r_sku = _resolve_col(rdf, *grain.product_id_columns)
            r_name = _resolve_col(rdf, "FULL_NAME_U", "FULL_NAME", *grain.display_name_columns)
            if not r_sku or not r_name:
                continue
            n = int(rdf[r_sku].nunique())
            if n > best_n:
                best_n = n
                best_ref = str(ref)
        if best_ref:
            rdf = working_set.get(best_ref).frame()
            r_sku = _resolve_col(rdf, *grain.product_id_columns)
            r_name = _resolve_col(rdf, "FULL_NAME_U", "FULL_NAME", *grain.display_name_columns)
            assert r_sku and r_name
            lookup = rdf[[r_sku, r_name]].drop_duplicates(r_sku)
            lookup = lookup.rename(columns={r_sku: sku_col, r_name: "FULL_NAME_U"})
            df = df.merge(lookup, on=sku_col, how="left")

    df = _trim_export_columns(df)
    # Sort by bill id when present.
    bill_col = _resolve_col(df, *grain.bill_id_columns)
    if bill_col:
        df = df.sort_values(by=[bill_col] + ([sku_col] if sku_col and sku_col in df.columns else []))

    bills_as = "export_bills"
    handle = working_set.get(bill_ref)
    working_set.save_frame(
        bills_as,
        df,
        role=getattr(handle, "role", None) or "fact",
        source="export_prepare",
        parents=[bill_ref],
    )
    # Decode likely mojibake text columns before export — never *_U (already Unicode).
    from project_core.text.tcvn3 import is_unicode_text_column

    text_cols = [
        c
        for c in df.columns
        if not is_unicode_text_column(str(c))
        and str(c).upper()
        in set(grain.customer_profile_columns)
        | set(grain.display_name_columns)
        | {"FULL_NAME", "CUST_NAME"}
    ]
    if text_cols:
        decoded = execute_op(
            working_set,
            "tcvn3_converter",
            {"dataset": bills_as, "columns": text_cols, "save_as": bills_as},
            out_dir=out,
        )
        if getattr(decoded, "status", None) != "ok":
            pass
    sheets["bills"] = bills_as

    if needs_customer_profile(brief):
        card_col = _resolve_col(df, "CARD_ID")
        if card_col:
            cust_cols = [card_col]
            for cand in ("CUST_NAME", "CUST_NAME_U", "PHONE", "MOBI", "CUST_ID"):
                col = _resolve_col(df, cand)
                if col and col not in cust_cols:
                    cust_cols.append(col)
            cust_df = df.loc[:, cust_cols].drop_duplicates(subset=[card_col])
            cust_df = cust_df.loc[_nonempty_mask(cust_df[card_col])].copy()
            customers_as = "export_customers"
            working_set.save_frame(
                customers_as,
                cust_df,
                role="dim",
                source="export_prepare_customers",
                parents=[bills_as],
            )
            cust_text = [
                c
                for c in cust_df.columns
                if not is_unicode_text_column(str(c))
                and str(c).upper() in set(grain.customer_profile_columns) | {"CUST_NAME"}
            ]
            if cust_text:
                execute_op(
                    working_set,
                    "tcvn3_converter",
                    {"dataset": customers_as, "columns": cust_text, "save_as": customers_as},
                    out_dir=out,
                )
            sheets["customers"] = customers_as

    return sheets


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
        # Keep companion bill lines when the frame already includes other SKUs
        # on the same bills (expanded basket) — only narrow pure product-only frames.
        keep_companions = False
        if scope_ids and len(scoped) < len(src_df):
            part = _partition_key_column(src_df)
            if part is not None and frame_has_bill_grain(src_df):
                present = set(src_df[part].astype(str)) & set(scope_ids)
                extras = set(src_df[part].astype(str)) - set(scope_ids)
                keep_companions = bool(present and extras)
        if len(scoped) == 0:
            # Keep source — coverage will flag product_codes_missing.
            pass
        elif keep_companions:
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


def _working_set_has_expanded_companion(
    working_set: DatasetWorkingSet,
    scope_ids: list[str] | set[str],
) -> bool:
    scope = {str(x) for x in scope_ids}
    if not scope:
        return False
    for ref in working_set.refs():
        try:
            other = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if other is None or len(other) == 0 or not frame_has_bill_grain(other):
            continue
        opart = _partition_key_column(other)
        if opart is None:
            continue
        oseries = other[opart].astype(str)
        if (set(oseries) & scope) and (set(oseries) - scope):
            return True
    return False


def primary_deliverable_frame(
    working_set: DatasetWorkingSet,
    *,
    brief: AnalysisBrief | None = None,
    product_codes: list[str] | None = None,
) -> tuple[pd.DataFrame | None, str | None]:
    """Prefer exported Excel (first/primary sheet); else prefer_export ranking."""
    candidates: list[str] = []
    for path in list(getattr(working_set, "excel_artifacts", None) or []) + list(
        working_set.artifact_paths or []
    ):
        if str(path).lower().endswith((".xlsx", ".xls", ".xlsm")):
            candidates.append(str(path))
    for path in candidates:
        try:
            xl = pd.ExcelFile(path)
            # Prefer a sheet that already looks like the analytical grain when present;
            # otherwise the first sheet — no hard-coded domain sheet names.
            sheet = xl.sheet_names[0]
            for name in xl.sheet_names:
                try:
                    probe = pd.read_excel(path, sheet_name=name, nrows=5)
                except Exception:  # noqa: BLE001
                    continue
                if brief is not None and needs_bill_deliverable(brief) and frame_has_bill_grain(probe):
                    sheet = name
                    break
                if brief is not None and not needs_bill_deliverable(brief) and len(probe) <= 50:
                    sheet = name
                    break
            return pd.read_excel(path, sheet_name=sheet), path
        except Exception:  # noqa: BLE001
            continue

    needs_bill = needs_bill_deliverable(brief) if brief is not None else False
    preferred = prefer_export_dataset_ref(
        working_set,
        needs_bill=needs_bill,
        product_codes=product_codes,
    )
    if preferred and working_set.has(preferred):
        try:
            return working_set.get(preferred).frame(), preferred
        except Exception:  # noqa: BLE001
            pass

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
        if df is None or len(df) == 0:
            continue
        cols = _cols_upper(df)
        role = str(getattr(handle, "role", None) or "")
        # Higher score wins — prefer bill grain + companion breadth over tiny product-only.
        score = 0
        if cols & set(grain.bill_id_columns):
            score += 1000
            score += min(len(df), 500)
        if cols & set(grain.product_id_columns):
            score += 100
        if dataset_looks_like_product_catalog(df, role=role):
            score -= 5000
        if best is None or score > best[0]:
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

    df, source = primary_deliverable_frame(
        working_set,
        brief=brief,
        product_codes=product_codes,
    )
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
        needs_bills = needs_bill_deliverable(brief)
        if needs_bills and not is_bill_frame:
            gaps.append("missing_bill_evidence_columns")
        if needs_bills and dataset_looks_like_product_catalog(df):
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
                # Extra SKUs are only a scope gap for top-N product ranking.
                # Bill-basket briefs intentionally keep companion lines.
                elif n_limit is not None and len(extras) > max(3, len(scope_ids) * 2):
                    gaps.append(f"product_scope_extra_skus:{len(extras)}")
            elif unique_n > max(len(codes) * 3, 10):
                gaps.append(f"product_scope_mismatch:got_{unique_n}_skus_want_~{len(codes)}")

    # When bill grain exists and resolve pins SKUs, product-only line exports miss
    # companion items — flag so finalize stays partial / planner can expand.
    scope_ids = resolved_sku_ids_from_working_set(working_set, product_codes)
    if (
        df is not None
        and is_bill_frame
        and scope_ids
        and _partition_key_column(df) is not None
    ):
        part = _partition_key_column(df)
        assert part is not None
        series = df[part].astype(str)
        present = set(series) & set(scope_ids)
        extras = set(series) - set(scope_ids)
        if present and not extras:
            if _working_set_has_expanded_companion(working_set, scope_ids):
                gaps.append("product_only_lines_when_expanded_available")
            else:
                caveats.append("product_only_bill_lines")

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
            "product_only_lines_when_expanded_available",
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
