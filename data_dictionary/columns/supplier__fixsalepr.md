---
semantic_key: supplier__fixsalepr
title: Fixsalepr (SUPPLIER)
display_names:
- FIXSALEPR
kind: measure
tables:
- ref: db2:supplier
  column: FIXSALEPR
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Fixsalepr (SUPPLIER)

**Semantic key:** `supplier__fixsalepr` · **Cột vật lý:** `FIXSALEPR`

## Ý nghĩa nghiệp vụ

Cờ giá bán cố định do NCC quy định — POS không tự điều chỉnh RTPRICE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `FIXSALEPR` | numeric | Chỉ số đo lường (fixsalepr) trên master nhà cung cấp |
