---
semantic_key: deduct
title: deduct
display_names:
- DEDUCT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: DEDUCT
  type: numeric
- ref: db2:transhdr
  column: DEDUCT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# deduct

**Semantic key:** `deduct` · **Cột vật lý:** `DEDUCT`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (deduct) — dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `DEDUCT` | numeric | Chỉ số đo lường (deduct) trên header bill đã archive |
| `db2:transhdr` | `DEDUCT` | numeric | Chỉ số đo lường (deduct) trên header bill bán lẻ |
