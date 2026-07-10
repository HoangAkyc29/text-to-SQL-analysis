---
semantic_key: st_order__ordp_qty
title: Số lượng (ST_ORDER)
display_names:
- ORDP_QTY
kind: measure
tables:
- ref: db2:st_order
  column: ORDP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngORDP_QTY
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (ST_ORDER)

**Semantic key:** `st_order__ordp_qty` · **Cột vật lý:** `ORDP_QTY`

## Ý nghĩa nghiệp vụ

Số lượng đặt theo pack / đơn vị đặt hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `ORDP_QTY` | numeric | Số lượngORDP_QTY |

## Ghi chú thêm

- Số lượngORDP_QTY
