---
semantic_key: hissppr__spprice
title: Giá khuyến mãi / giá đặc biệt (HISSPPR)
display_names:
- SPPRICE
kind: measure
tables:
- ref: db2:hissppr
  column: SPPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá mua NCC
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giá khuyến mãi / giá đặc biệt (HISSPPR)

**Semantic key:** `hissppr__spprice` · **Cột vật lý:** `SPPRICE`

## Ý nghĩa nghiệp vụ

Giá khuyến mãi / giá đặc biệt — bảng HISSPPR.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:hissppr` | `SPPRICE` | numeric | Giá mua NCC |

## Ghi chú thêm

- Giá mua NCC
