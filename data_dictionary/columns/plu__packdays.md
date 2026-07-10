---
semantic_key: plu__packdays
title: Packdays (PLU)
display_names:
- PACKDAYS
kind: measure
tables:
- ref: db2:plu
  column: PACKDAYS
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Packdays (PLU)

**Semantic key:** `plu__packdays` · **Cột vật lý:** `PACKDAYS`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (packdays) — bảng PLU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:plu` | `PACKDAYS` | numeric | Chỉ số đo lường (packdays) trên bảng plu |
