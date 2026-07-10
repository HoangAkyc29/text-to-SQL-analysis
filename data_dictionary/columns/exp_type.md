---
semantic_key: exp_type
title: exp type
display_names:
- EXP_TYPE
kind: text
tables:
- ref: db1:transhdr_arc
  column: EXP_TYPE
  type: char
- ref: db2:transhdr
  column: EXP_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Xuất / export: EXP_TYPE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# exp type

**Semantic key:** `exp_type` · **Cột vật lý:** `EXP_TYPE`

## Ý nghĩa nghiệp vụ

Xuất / export: EXP_TYPE. Dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `EXP_TYPE` | char | Xuất / export: EXP_TYPE |
| `db2:transhdr` | `EXP_TYPE` | char | Xuất / export: EXP_TYPE |
