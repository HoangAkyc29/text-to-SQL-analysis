---
semantic_key: grp_id
title: Mã nhóm phân loại (GRP_ID)
display_names:
- grp_id
- GRP_ID
kind: identifier
tables:
- ref: db2:customer
  column: GRP_ID
  type: char
- ref: db2:partner
  column: GRP_ID
  type: char
- ref: db2:sku_def
  column: GRP_ID
  type: varchar
- ref: db2:supplier
  column: GRP_ID
  type: char
- ref: db2:webrpt_inventory_daily
  column: grp_id
  type: varchar
- ref: db2:webrpt_sales_sku_daily
  column: grp_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã nhóm
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã nhóm phân loại (GRP_ID)

**Semantic key:** `grp_id` · **Cột vật lý:** `grp_id`, `GRP_ID`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `GRP_ID` | char | Mã nhóm |
| `db2:partner` | `GRP_ID` | char | Mã nhóm |
| `db2:sku_def` | `GRP_ID` | varchar | Mã nhóm |
| `db2:supplier` | `GRP_ID` | char | Mã nhóm |
| `db2:webrpt_inventory_daily` | `grp_id` | varchar | Mã nhóm hàng |
| `db2:webrpt_sales_sku_daily` | `grp_id` | varchar | Mã nhóm hàng |

## Ghi chú thêm

- Mã nhóm
