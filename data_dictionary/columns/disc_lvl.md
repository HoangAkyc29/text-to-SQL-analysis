---
semantic_key: disc_lvl
title: Mức chiết khấu được hưởng (DISC_LVL)
display_names:
- DISC_LVL
kind: measure
tables:
- ref: db2:crd_info
  column: DISC_LVL
  type: numeric
- ref: db2:cscard
  column: DISC_LVL
  type: numeric
- ref: db2:customer
  column: DISC_LVL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Mức chiết khấu
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mức chiết khấu được hưởng (DISC_LVL)

**Semantic key:** `disc_lvl` · **Cột vật lý:** `DISC_LVL`

## Ý nghĩa nghiệp vụ

Mức chiết khấu. Dùng trong Loyalty / thẻ (CRD_INFO, CSCARD); Master / danh mục (CUSTOMER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `DISC_LVL` | numeric | Mức chiết khấu |
| `db2:cscard` | `DISC_LVL` | numeric | Mức chiết khấu / hạng thẻ |
| `db2:customer` | `DISC_LVL` | numeric | Mức chiết khấu |
