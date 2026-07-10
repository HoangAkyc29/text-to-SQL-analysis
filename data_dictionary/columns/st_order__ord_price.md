---
semantic_key: st_order__ord_price
title: Đơn giá (ST_ORDER)
display_names:
- ORD_PRICE
kind: measure
tables:
- ref: db2:st_order
  column: ORD_PRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá đặt hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Đơn giá (ST_ORDER)

**Semantic key:** `st_order__ord_price` · **Cột vật lý:** `ORD_PRICE`

## Ý nghĩa nghiệp vụ

Đơn giá đặt hàng trên đơn nội bộ — khác RTPRICE master.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `ORD_PRICE` | numeric | Giá đặt hàng |
