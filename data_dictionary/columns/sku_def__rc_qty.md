---
semantic_key: sku_def__rc_qty
title: Số lượng (SKU_DEF)
display_names:
- RC_QTY
kind: measure
tables:
- ref: db2:sku_def
  column: RC_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngRC_QTY
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (SKU_DEF)

**Semantic key:** `sku_def__rc_qty` · **Cột vật lý:** `RC_QTY`

## Ý nghĩa nghiệp vụ

Số lượng reorder point — ngưỡng đặt hàng lại.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `RC_QTY` | numeric | Số lượngRC_QTY |

## Ghi chú thêm

- Số lượngRC_QTY
