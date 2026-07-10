---
semantic_key: asso_type
title: Loại combo (ASSO_TYPE)
display_names:
- ASSO_TYPE
kind: text
tables:
- ref: db2:asso_inf
  column: ASSO_TYPE
  type: char
- ref: db2:assolst
  column: ASSO_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại combo
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Loại combo (ASSO_TYPE)

**Semantic key:** `asso_type` · **Cột vật lý:** `ASSO_TYPE`

## Ý nghĩa nghiệp vụ

Loại combo (fixed bundle, pick-N, …) trên ASSOLST/ASSO_INF.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `ASSO_TYPE` | char | Loại combo |
| `db2:assolst` | `ASSO_TYPE` | char | Loại combo |
