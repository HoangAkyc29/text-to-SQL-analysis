---
semantic_key: margin
title: Biên lợi nhuận (%) (MARGIN)
display_names:
- MARGIN
kind: measure
tables:
- ref: db2:asso_inf
  column: MARGIN
  type: numeric
- ref: db2:assolst
  column: MARGIN
  type: numeric
- ref: db2:sku_def
  column: MARGIN
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Biên lợi nhuận (%) (MARGIN)

**Semantic key:** `margin` · **Cột vật lý:** `MARGIN`

## Ý nghĩa nghiệp vụ

Biên lợi nhuận (%) — dùng trong Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `MARGIN` | numeric | Biên lợi nhuận (%) trên chi tiết thành phần combo |
| `db2:assolst` | `MARGIN` | numeric | Biên lợi nhuận (%) trên master combo / bundle |
| `db2:sku_def` | `MARGIN` | numeric | Biên lợi nhuận (%) trên master sản phẩm (SKU) |
