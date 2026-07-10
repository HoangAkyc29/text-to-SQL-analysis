---
semantic_key: st_order__dlv_qty
title: Số lượng dlv (ST_ORDER)
display_names:
- DLV_QTY
kind: measure
tables:
- ref: db2:st_order
  column: DLV_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng đã giao
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng dlv (ST_ORDER)

**Semantic key:** `st_order__dlv_qty` · **Cột vật lý:** `DLV_QTY`

## Ý nghĩa nghiệp vụ

Số lượng đã giao / đã nhận so với đơn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `DLV_QTY` | numeric | Số lượng đã giao |
