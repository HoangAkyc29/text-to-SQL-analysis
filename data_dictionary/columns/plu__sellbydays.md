---
semantic_key: plu__sellbydays
title: Sellbydays (PLU)
display_names:
- SELLBYDAYS
kind: measure
tables:
- ref: db2:plu
  column: SELLBYDAYS
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Sellbydays (PLU)

**Semantic key:** `plu__sellbydays` · **Cột vật lý:** `SELLBYDAYS`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (sellbydays) — bảng PLU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:plu` | `SELLBYDAYS` | numeric | Chỉ số đo lường (sellbydays) trên bảng plu |
