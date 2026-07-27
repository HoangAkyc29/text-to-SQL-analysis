"""analysis_grain.yaml loads for deliverable guards."""

from __future__ import annotations

import pytest

from project_core.domain.schema.analysis_grain import clear_analysis_grain_cache, load_analysis_grain

pytestmark = pytest.mark.unit


def test_load_analysis_grain_from_dictionary():
    clear_analysis_grain_cache()
    grain = load_analysis_grain()
    assert "SKU_ID" in grain.product_id_columns or "SKU_CODE" in grain.product_id_columns
    assert "TRANS_NUM" in grain.bill_id_columns
    assert "catalog" in grain.catalog_roles
    assert "FULL_NAME" in grain.display_name_columns
