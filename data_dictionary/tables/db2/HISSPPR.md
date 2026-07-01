---
logical_table: HISSPPR
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Lịch sử giá mua NCC.
column_count: 15
---

# HISSPPR

Lịch sử giá mua NCC.

| column | type | description |
|--------|------|-------------|
| DATE | datetime | Cột DATE |
| TIME | char | Cột TIME |
| SKU_ID | char | Mã sản phẩm nội bộ |
| SUPP_ID | char | Mã nhà cung cấp |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| BASE_UNIT | char | Đơn vị cơ sở |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| LASTSPPR | numeric | Giá mua NCC gần nhất |
| SPPRICE | numeric | Giá mua NCC |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| PCPR_CODE | char | MãPCPR_CODE |
| TAX_CODE | char | Mã thuế |
| COMP_ID | char | Mã công ty |
