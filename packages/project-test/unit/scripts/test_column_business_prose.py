"""Tests for column business prose (no sample dumps)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

from column_business_prose import compose_business_prose, compose_table_role  # noqa: E402
from column_dictionary_lib import ColumnOccurrence  # noqa: E402


def test_cust_name_prose_natural():
    text = compose_business_prose(
        semantic_key="cust_name",
        display_names=["CUST_NAME"],
        kind="text",
        tables=[
            {"ref": "db2:customer", "column": "CUST_NAME", "type": "nvarchar"},
            {"ref": "db2:inv_iss", "column": "CUST_NAME", "type": "nvarchar"},
        ],
        occurrences=[
            ColumnOccurrence("db2:customer", "CUSTOMER", "db2", "CUST_NAME", "nvarchar", "Tên khách hàng"),
        ],
    )
    assert "Quan sát" not in text
    assert "top" not in text.lower()
    assert "khách hàng" in text.lower()
    assert "đăng ký" in text.lower() or "master" in text.lower()


def test_dept_id_not_generic_column_dump():
    text = compose_business_prose(
        semantic_key="dept_id",
        display_names=["DEPT_ID"],
        kind="identifier",
        tables=[
            {"ref": "db2:sku_def", "column": "DEPT_ID", "type": "char"},
            {"ref": "db2:supplier", "column": "DEPT_ID", "type": "char"},
        ],
    )
    assert "Cột DEPT_ID trên" not in text
    assert "ngành hàng" in text.lower()


def test_table_role_uses_nuance():
    role = compose_table_role("CUSTOMER", "CUST_NAME", table_description="Tên khách hàng", kind="text")
    assert "master" in role.lower() or "đăng ký" in role.lower()


def test_vat_amt_prose_has_grain_not_table_dump():
    tables = [
        {"ref": "db2:strans", "column": "VAT_AMT", "type": "numeric"},
        {"ref": "db2:transhdr", "column": "VAT_AMT", "type": "numeric"},
        {"ref": "db2:crdtrans", "column": "VAT_AMT", "type": "numeric"},
    ]
    text = compose_business_prose(
        semantic_key="vat_amt",
        display_names=["VAT_AMT"],
        kind="measure",
        tables=tables,
        facts=["Tiền thuế VAT"],
    )
    assert "Xuất hiện trên" not in text
    assert "STRANS" in text or "dòng bán" in text.lower()
    assert "TRANSHDR" in text or "bill" in text.lower()
    assert "GTGT" in text or "VAT" in text


def test_vat_amt_table_role_per_table():
    role = compose_table_role("STRANS", "VAT_AMT", table_description="Tiền thuế VAT", kind="measure")
    assert "dòng" in role.lower() or "POS" in role
    role_hdr = compose_table_role("TRANSHDR", "VAT_AMT", table_description="Tiền thuế VAT", kind="measure")
    assert "bill" in role_hdr.lower() or "header" in role_hdr.lower()


def test_infer_column_title_vat():
    from column_business_prose import infer_column_title

    assert "GTGT" in infer_column_title("vat_amt", ["VAT_AMT"])


def test_stk_dtl_begin_qty_prose():
    text = compose_business_prose(
        semantic_key="stk_dtl__begin_qty",
        display_names=["BEGIN_QTY"],
        kind="measure",
        tables=[{"ref": "db2:stk_dtl", "column": "BEGIN_QTY", "type": "numeric"}],
    )
    assert "đầu kỳ" in text.lower()
    assert "STK_DTL" in text


def test_rdiscinf_gift_prose():
    text = compose_business_prose(
        semantic_key="rdiscinf__gift",
        display_names=["GIFT"],
        kind="flag",
        tables=[{"ref": "db2:rdiscinf", "column": "GIFT", "type": "bit"}],
    )
    assert "quà" in text.lower()


def test_sku_def_full_name_prose():
    text = compose_business_prose(
        semantic_key="sku_def__full_name",
        display_names=["FULL_NAME"],
        kind="text",
        tables=[{"ref": "db2:sku_def", "column": "FULL_NAME", "type": "nvarchar"}],
    )
    assert "sản phẩm" in text.lower() or "SKU" in text
