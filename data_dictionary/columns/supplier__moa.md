---
semantic_key: supplier__moa
title: Giá trị đơn đặt tối thiểu (MOA) (SUPPLIER)
display_names:
- MOA
kind: measure
tables:
- ref: db2:supplier
  column: MOA
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giá trị đơn đặt tối thiểu (MOA) (SUPPLIER)

**Semantic key:** `supplier__moa` · **Cột vật lý:** `MOA`

## Ý nghĩa nghiệp vụ

Minimum Order Amount — giá trị đơn đặt tối thiểu với NCC.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `MOA` | numeric | Giá trị đơn đặt tối thiểu (moa) trên master nhà cung cấp |
