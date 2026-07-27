"""Load analysis grain roles from data_dictionary (not hardcoded in guards)."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from project_core.paths import ROOT


@dataclass(frozen=True)
class AnalysisGrain:
    product_id_columns: tuple[str, ...] = ("SKU_ID", "SKU_CODE")
    bill_id_columns: tuple[str, ...] = ("TRANS_NUM", "BILL_NO", "TRANS_ID")
    catalog_roles: tuple[str, ...] = ("catalog", "product", "products")
    catalog_ref_substrings: tuple[str, ...] = (
        "resolved_sku",
        "resolved_product",
        "products",
        "sku_def",
    )
    display_name_columns: tuple[str, ...] = (
        "FULL_NAME",
        "SKU_NAME",
        "PRODUCT_NAME",
        "TEN_HANG",
        "NAME",
        "ITEM_NAME",
        "DESCRIPTION",
    )


def _as_upper_tuple(raw: Any, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(raw, list) or not raw:
        return fallback
    out = tuple(str(x).strip().upper() for x in raw if str(x).strip())
    return out or fallback


def _as_lower_tuple(raw: Any, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(raw, list) or not raw:
        return fallback
    out = tuple(str(x).strip().lower() for x in raw if str(x).strip())
    return out or fallback


@lru_cache(maxsize=1)
def load_analysis_grain() -> AnalysisGrain:
    path = ROOT / "data_dictionary" / "analysis_grain.yaml"
    defaults = AnalysisGrain()
    if not path.is_file():
        return defaults
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError:
        return defaults
    if not isinstance(data, dict):
        return defaults
    return AnalysisGrain(
        product_id_columns=_as_upper_tuple(data.get("product_id_columns"), defaults.product_id_columns),
        bill_id_columns=_as_upper_tuple(data.get("bill_id_columns"), defaults.bill_id_columns),
        catalog_roles=_as_lower_tuple(data.get("catalog_roles"), defaults.catalog_roles),
        catalog_ref_substrings=_as_lower_tuple(
            data.get("catalog_ref_substrings"), defaults.catalog_ref_substrings
        ),
        display_name_columns=_as_upper_tuple(
            data.get("display_name_columns"), defaults.display_name_columns
        ),
    )


def clear_analysis_grain_cache() -> None:
    load_analysis_grain.cache_clear()
