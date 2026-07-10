---
semantic_key: imp_type
title: imp type
display_names:
- IMP_TYPE
kind: text
tables:
- ref: db1:transhdr_arc
  column: IMP_TYPE
  type: char
- ref: db2:transhdr
  column: IMP_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Nhập / import: IMP_TYPE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# imp type

**Semantic key:** `imp_type` · **Cột vật lý:** `IMP_TYPE`

## Ý nghĩa nghiệp vụ

Nhập / import: IMP_TYPE. Dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `IMP_TYPE` | char | Nhập / import: IMP_TYPE |
| `db2:transhdr` | `IMP_TYPE` | char | Nhập / import: IMP_TYPE |
