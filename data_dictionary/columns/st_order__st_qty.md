---
semantic_key: st_order__st_qty
title: Số lượng (ST_ORDER)
display_names:
- ST_QTY
kind: measure
tables:
- ref: db2:st_order
  column: ST_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngST_QTY
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (ST_ORDER)

**Semantic key:** `st_order__st_qty` · **Cột vật lý:** `ST_QTY`

## Ý nghĩa nghiệp vụ

Số lượng tồn / còn lại trên đơn ST_ORDER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `ST_QTY` | numeric | Số lượngST_QTY |

## Ghi chú thêm

- Số lượngST_QTY
