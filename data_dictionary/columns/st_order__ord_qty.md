---
semantic_key: st_order__ord_qty
title: Số lượng đặt hàng (ST_ORDER)
display_names:
- ORD_QTY
kind: measure
tables:
- ref: db2:st_order
  column: ORD_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng đặt
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng đặt hàng (ST_ORDER)

**Semantic key:** `st_order__ord_qty` · **Cột vật lý:** `ORD_QTY`

## Ý nghĩa nghiệp vụ

Số lượng đặt hàng trên đơn ST_ORDER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `ORD_QTY` | numeric | Số lượng đặt |
