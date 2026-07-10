---
semantic_key: st_order__sal_qty
title: Số lượng sal (ST_ORDER)
display_names:
- SAL_QTY
kind: measure
tables:
- ref: db2:st_order
  column: SAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng bán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng sal (ST_ORDER)

**Semantic key:** `st_order__sal_qty` · **Cột vật lý:** `SAL_QTY`

## Ý nghĩa nghiệp vụ

Số lượng đã bán / xuất từ đơn nội bộ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `SAL_QTY` | numeric | Số lượng bán |

## Ghi chú thêm

- Số lượng bán
