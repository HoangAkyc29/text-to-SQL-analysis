---
semantic_key: partner__payday
title: Payday (PARTNER)
display_names:
- PAYDAY
kind: measure
tables:
- ref: db2:partner
  column: PAYDAY
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Payday (PARTNER)

**Semantic key:** `partner__payday` · **Cột vật lý:** `PAYDAY`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (payday) — đối tác / khách B2B.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `PAYDAY` | numeric | Chỉ số đo lường (payday) trên đối tác / khách B2B |
