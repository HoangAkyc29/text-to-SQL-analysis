---
logical_table: ASSO_INF
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Thành phần trong combo/bundle.
column_count: 20
---

# ASSO_INF

Thành phần trong combo/bundle.

| column | type | description |
|--------|------|-------------|
| ASSO_ID | char | Mã combo/bundle |
| ASSO_TYPE | char | Loại combo |
| IMPORT | bit | Cờ nhập / import |
| IDX | numeric | Số thứ tự dòng trong chứng từ |
| SKU_ID | char | Mã sản phẩm nội bộ |
| PLU_CODE | char | Mã PLU |
| ITEM_TYPE | char | Loại dòng hàng |
| MERC_TYPE | char | Loại hàng hóa |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| BASE_UNIT | char | Đơn vị cơ sở |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| QTY | numeric | Số lượng |
| PRICE | numeric | Đơn giá |
| RTPRICE | numeric | Giá bán lẻ |
| ZONE_CODE | char | MãZONE_CODE |
| MARGIN | numeric | Cột MARGIN |
| TAX_CODE | char | Mã thuế |
| TAX_RATE | numeric | Thuế suất |
| RATIO | numeric | Cột RATIO |
| STATUS | bit | Trạng thái active/duyệt |
