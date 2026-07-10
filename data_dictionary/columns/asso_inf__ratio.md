---
semantic_key: asso_inf__ratio
title: Ratio (ASSO_INF)
display_names:
- RATIO
kind: measure
tables:
- ref: db2:asso_inf
  column: RATIO
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ratio (ASSO_INF)

**Semantic key:** `asso_inf__ratio` · **Cột vật lý:** `RATIO`

## Ý nghĩa nghiệp vụ

Tỷ lệ thành phần trong combo — số lượng / % so với bundle header ASSOLST.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `RATIO` | numeric | Chỉ số đo lường (ratio) trên chi tiết thành phần combo |
