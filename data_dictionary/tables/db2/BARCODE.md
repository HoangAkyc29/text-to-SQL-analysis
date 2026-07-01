---
logical_table: BARCODE
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Barcode phụ và quy đổi đơn vị cho SKU.
column_count: 7
---

# BARCODE

Barcode phụ và quy đổi đơn vị cho SKU.

| column | type | description |
|--------|------|-------------|
| BARCODE | char | Mã vạch |
| SKU_ID | char | Mã sản phẩm nội bộ |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| DESCRIPT | nvarchar | Mô tả |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| ISDEFAULT | bit | Mặc định |
