---
logical_table: PLU
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Giá bán theo PLU/quầy và hiệu lực.
column_count: 19
---

# PLU

Giá bán theo PLU/quầy và hiệu lực.

| column | type | description |
|--------|------|-------------|
| PLU_CODE | varchar | Mã PLU |
| SKU_ID | char | Mã sản phẩm nội bộ |
| MERC_TYPE | char | Loại hàng hóa |
| USEBYDAYS | numeric | Cột USEBYDAYS |
| PACKDAYS | numeric | Cột PACKDAYS |
| SELLBYDAYS | numeric | Cột SELLBYDAYS |
| LBL_TYPE | char | Cột LBL_TYPE |
| CYS | char | Loại tiền (VND) |
| RTPRICE | numeric | Giá bán lẻ |
| LASTRTPR | numeric | Giá bán lẻ gần nhất |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| VAT_INCL | bit | Giá đã gồm VAT |
| OPEN_DATE | datetime | Ngày mở / tạo |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| FR_DATE | datetime | NgàyFR_DATE |
| TO_DATE | datetime | NgàyTO_DATE |
| STATUS | bit | Trạng thái active/duyệt |
