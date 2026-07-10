---
semantic_key: deposit
title: deposit
display_names:
- DEPOSIT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: DEPOSIT
  type: numeric
- ref: db2:transhdr
  column: DEPOSIT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# deposit

**Semantic key:** `deposit` · **Cột vật lý:** `DEPOSIT`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (deposit) — dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `DEPOSIT` | numeric | Chỉ số đo lường (deposit) trên header bill đã archive |
| `db2:transhdr` | `DEPOSIT` | numeric | Chỉ số đo lường (deposit) trên header bill bán lẻ |
