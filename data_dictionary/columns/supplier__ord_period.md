---
semantic_key: supplier__ord_period
title: Ord Period (SUPPLIER)
display_names:
- ORD_PERIOD
kind: measure
tables:
- ref: db2:supplier
  column: ORD_PERIOD
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ord Period (SUPPLIER)

**Semantic key:** `supplier__ord_period` · **Cột vật lý:** `ORD_PERIOD`

## Ý nghĩa nghiệp vụ

Chu kỳ đặt hàng mặc định (ngày/tuần) gắn NCC — lập lịch replenishment.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `ORD_PERIOD` | numeric | Chỉ số đo lường (ord period) trên master nhà cung cấp |
