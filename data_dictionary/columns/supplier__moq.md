---
semantic_key: supplier__moq
title: Số lượng đặt hàng tối thiểu (MOQ) (SUPPLIER)
display_names:
- MOQ
kind: measure
tables:
- ref: db2:supplier
  column: MOQ
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng đặt hàng tối thiểu (MOQ) (SUPPLIER)

**Semantic key:** `supplier__moq` · **Cột vật lý:** `MOQ`

## Ý nghĩa nghiệp vụ

Minimum Order Quantity — số lượng đặt hàng tối thiểu với NCC.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `MOQ` | numeric | Số lượng đặt hàng tối thiểu (moq) trên master nhà cung cấp |
