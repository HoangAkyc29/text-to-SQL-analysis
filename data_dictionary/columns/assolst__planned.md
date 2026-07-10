---
semantic_key: assolst__planned
title: Planned (ASSOLST)
display_names:
- Planned
kind: flag
tables:
- ref: db2:assolst
  column: Planned
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Planned (ASSOLST)

**Semantic key:** `assolst__planned` · **Cột vật lý:** `Planned`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (planned) — master combo / bundle.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:assolst` | `Planned` | bit | Cờ / trạng thái (planned) trên master combo / bundle |
