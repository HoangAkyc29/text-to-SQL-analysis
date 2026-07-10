---
semantic_key: imp_id
title: imp id
display_names:
- IMP_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: IMP_ID
  type: char
- ref: db2:transhdr
  column: IMP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Nhập / import: IMP_ID'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# imp id

**Semantic key:** `imp_id` · **Cột vật lý:** `IMP_ID`

## Ý nghĩa nghiệp vụ

Nhập / import: IMP_ID. Dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `IMP_ID` | char | Nhập / import: IMP_ID |
| `db2:transhdr` | `IMP_ID` | char | Nhập / import: IMP_ID |
