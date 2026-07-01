---
logical_table: STK_DTL
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Sổ chi tiết tồn kho theo kỳ (nhập/xuất/bán/điều chuyển).
column_count: 63
---

# STK_DTL

Sổ chi tiết tồn kho theo kỳ (nhập/xuất/bán/điều chuyển).

| column | type | description |
|--------|------|-------------|
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| SKU_ID | char | Mã sản phẩm nội bộ |
| BEGIN_QTY | numeric | Tồn đầu kỳ — số lượng |
| BEGIN_AMT | numeric | Tồn đầu kỳ — giá trị |
| FRSUPP_QTY | numeric | Đầu kỳ — movement: FRSUPP_QTY |
| FRSUPP_AMT | numeric | Đầu kỳ — movement: FRSUPP_AMT |
| FRSUPP_SUR | numeric | Đầu kỳ — movement: FRSUPP_SUR |
| FRSUPP_VAT | numeric | Đầu kỳ — movement: FRSUPP_VAT |
| FRSUPP_DIS | numeric | Đầu kỳ — movement: FRSUPP_DIS |
| FRSUPP_COM | numeric | Đầu kỳ — movement: FRSUPP_COM |
| FRDEAL_QTY | numeric | Đầu kỳ — movement: FRDEAL_QTY |
| FRDEAL_AMT | numeric | Đầu kỳ — movement: FRDEAL_AMT |
| FRDEAL_SUR | numeric | Đầu kỳ — movement: FRDEAL_SUR |
| FRDEAL_VAT | numeric | Đầu kỳ — movement: FRDEAL_VAT |
| FRDEAL_DIS | numeric | Đầu kỳ — movement: FRDEAL_DIS |
| FRDEAL_COM | numeric | Đầu kỳ — movement: FRDEAL_COM |
| FRCUST_QTY | numeric | Đầu kỳ — movement: FRCUST_QTY |
| FRCUST_AMT | numeric | Đầu kỳ — movement: FRCUST_AMT |
| FRCUST_SUR | numeric | Đầu kỳ — movement: FRCUST_SUR |
| FRCUST_VAT | numeric | Đầu kỳ — movement: FRCUST_VAT |
| FRCUST_DIS | numeric | Đầu kỳ — movement: FRCUST_DIS |
| FRCUST_COM | numeric | Đầu kỳ — movement: FRCUST_COM |
| FRTRF_QTY | numeric | Đầu kỳ — movement: FRTRF_QTY |
| FRTRF_AMT | numeric | Đầu kỳ — movement: FRTRF_AMT |
| FRMUL_QTY | numeric | Đầu kỳ — movement: FRMUL_QTY |
| FRMUL_AMT | numeric | Đầu kỳ — movement: FRMUL_AMT |
| FRBAL_QTY | numeric | Đầu kỳ — movement: FRBAL_QTY |
| FRBAL_AMT | numeric | Đầu kỳ — movement: FRBAL_AMT |
| FRCQTY_QTY | numeric | Đầu kỳ — movement: FRCQTY_QTY |
| FRCQTY_AMT | numeric | Đầu kỳ — movement: FRCQTY_AMT |
| FRCAMT_QTY | numeric | Đầu kỳ — movement: FRCAMT_QTY |
| FRCAMT_AMT | numeric | Đầu kỳ — movement: FRCAMT_AMT |
| FRCAMT_SUR | numeric | Đầu kỳ — movement: FRCAMT_SUR |
| TOSUPP_QTY | numeric | Cuối kỳ — movement: TOSUPP_QTY |
| TOSUPP_AMT | numeric | Cuối kỳ — movement: TOSUPP_AMT |
| TOSUPP_SUR | numeric | Cuối kỳ — movement: TOSUPP_SUR |
| TOSUPP_VAT | numeric | Cuối kỳ — movement: TOSUPP_VAT |
| TOSUPP_DIS | numeric | Cuối kỳ — movement: TOSUPP_DIS |
| TOSUPP_COM | numeric | Cuối kỳ — movement: TOSUPP_COM |
| TODEAL_QTY | numeric | Cuối kỳ — movement: TODEAL_QTY |
| TODEAL_AMT | numeric | Cuối kỳ — movement: TODEAL_AMT |
| TODEAL_SUR | numeric | Cuối kỳ — movement: TODEAL_SUR |
| TODEAL_VAT | numeric | Cuối kỳ — movement: TODEAL_VAT |
| TODEAL_DIS | numeric | Cuối kỳ — movement: TODEAL_DIS |
| TODEAL_COM | numeric | Cuối kỳ — movement: TODEAL_COM |
| TOCUST_QTY | numeric | Cuối kỳ — movement: TOCUST_QTY |
| TOCUST_AMT | numeric | Cuối kỳ — movement: TOCUST_AMT |
| TOCUST_SUR | numeric | Cuối kỳ — movement: TOCUST_SUR |
| TOCUST_VAT | numeric | Cuối kỳ — movement: TOCUST_VAT |
| TOCUST_DIS | numeric | Cuối kỳ — movement: TOCUST_DIS |
| TOCUST_COM | numeric | Cuối kỳ — movement: TOCUST_COM |
| TOTRF_QTY | numeric | Cuối kỳ — movement: TOTRF_QTY |
| TOTRF_AMT | numeric | Cuối kỳ — movement: TOTRF_AMT |
| TOMUL_QTY | numeric | Cuối kỳ — movement: TOMUL_QTY |
| TOMUL_AMT | numeric | Cuối kỳ — movement: TOMUL_AMT |
| TOBAL_QTY | numeric | Cuối kỳ — movement: TOBAL_QTY |
| TOBAL_AMT | numeric | Cuối kỳ — movement: TOBAL_AMT |
| TOCQTY_QTY | numeric | Cuối kỳ — movement: TOCQTY_QTY |
| TOCQTY_AMT | numeric | Cuối kỳ — movement: TOCQTY_AMT |
| TOCAMT_QTY | numeric | Cuối kỳ — movement: TOCAMT_QTY |
| TOCAMT_AMT | numeric | Cuối kỳ — movement: TOCAMT_AMT |
| TOCAMT_SUR | numeric | Cuối kỳ — movement: TOCAMT_SUR |
| PRD_CODE | varchar | Mã kỳ tồn kho |
