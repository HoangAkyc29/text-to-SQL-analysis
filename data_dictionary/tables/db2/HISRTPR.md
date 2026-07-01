---
logical_table: HISRTPR
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Lịch sử giá bán lẻ theo ngày × SKU × cửa hàng.
column_count: 16
---

# HISRTPR

Lịch sử giá bán lẻ theo ngày × SKU × cửa hàng.

| column | type | description |
|--------|------|-------------|
| DATE | datetime | Cột DATE |
| TIME | char | Cột TIME |
| SKU_ID | char | Mã sản phẩm nội bộ |
| ZONE_CODE | char | MãZONE_CODE |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| BASE_UNIT | char | Đơn vị cơ sở |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| LASTRTPR | numeric | Giá bán lẻ gần nhất |
| RTPRICE | numeric | Giá bán lẻ |
| STK_QTY | numeric | Số lượng tồn / xuất kho |
| RTPRAMT | numeric | Cột RTPRAMT |
| SURP_PC | numeric | Cột SURP_PC |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| COMP_ID | char | Mã công ty |
| RTPR_CODE | char | MãRTPR_CODE |
