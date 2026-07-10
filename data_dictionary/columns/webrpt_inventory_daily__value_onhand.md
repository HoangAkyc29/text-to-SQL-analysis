---
semantic_key: webrpt_inventory_daily__value_onhand
title: Value Onhand (WEBRPT_INVENTORY_DAILY)
display_names:
- value_onhand
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: value_onhand
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Giá trị tồn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Value Onhand (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__value_onhand` · **Cột vật lý:** `value_onhand`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `value_onhand` | decimal | Giá trị tồn |

## Ghi chú thêm

- Giá trị tồn
