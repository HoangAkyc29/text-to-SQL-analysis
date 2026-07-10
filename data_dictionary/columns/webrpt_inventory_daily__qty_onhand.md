---
semantic_key: webrpt_inventory_daily__qty_onhand
title: Qty Onhand (WEBRPT_INVENTORY_DAILY)
display_names:
- qty_onhand
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: qty_onhand
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tồn kho hiện tại
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Qty Onhand (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__qty_onhand` · **Cột vật lý:** `qty_onhand`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `qty_onhand` | decimal | Tồn kho hiện tại |

## Ghi chú thêm

- Tồn kho hiện tại
