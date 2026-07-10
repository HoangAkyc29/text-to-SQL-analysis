---
semantic_key: exp_id
title: exp id
display_names:
- EXP_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: EXP_ID
  type: char
- ref: db2:transhdr
  column: EXP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Xuất / export: EXP_ID'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# exp id

**Semantic key:** `exp_id` · **Cột vật lý:** `EXP_ID`

## Ý nghĩa nghiệp vụ

Xuất / export: EXP_ID. Dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `EXP_ID` | char | Xuất / export: EXP_ID |
| `db2:transhdr` | `EXP_ID` | char | Xuất / export: EXP_ID |
