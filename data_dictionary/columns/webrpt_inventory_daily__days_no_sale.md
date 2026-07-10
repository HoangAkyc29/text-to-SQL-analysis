---
semantic_key: webrpt_inventory_daily__days_no_sale
title: Days No Sale (WEBRPT_INVENTORY_DAILY)
display_names:
- days_no_sale
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: days_no_sale
  type: int
join_with: []
related_semantic_keys: []
facts:
- Số ngày không bán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Days No Sale (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__days_no_sale` · **Cột vật lý:** `days_no_sale`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `days_no_sale` | int | Số ngày không bán |

## Ghi chú thêm

- Số ngày không bán
