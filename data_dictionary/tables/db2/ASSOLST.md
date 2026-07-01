---
logical_table: ASSOLST
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Header combo/bundle khuyến mãi.
column_count: 17
---

# ASSOLST

Header combo/bundle khuyến mãi.

| column | type | description |
|--------|------|-------------|
| ASSO_ID | char | Mã combo/bundle |
| ASSO_TYPE | char | Loại combo |
| DESCRIPT | nvarchar | Mô tả |
| FIX_RATIO | bit | Cột FIX_RATIO |
| IsProcess | bit | Cột IsProcess |
| REVERSE | bit | Cột REVERSE |
| Planned | bit | Cột Planned |
| Sale_Period | char | Cột Sale_Period |
| MARGIN | numeric | Cột MARGIN |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| SKU | bit | Cột SKU |
| MBC | bit | Cột MBC |
| ISS_DATE | datetime | NgàyISS_DATE |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| STATUS | bit | Trạng thái active/duyệt |
