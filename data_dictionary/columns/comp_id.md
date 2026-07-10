---
semantic_key: comp_id
title: Mã công ty / pháp nhân (COMP_ID)
display_names:
- COMP_ID
kind: identifier
tables:
- ref: db2:rdiscinf
  column: COMP_ID
  type: char
- ref: db2:supplier
  column: COMP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã công ty
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã công ty / pháp nhân (COMP_ID)

**Semantic key:** `comp_id` · **Cột vật lý:** `COMP_ID`

## Ý nghĩa nghiệp vụ

Mã công ty. Dùng trong Master / danh mục (SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `COMP_ID` | char | Mã công ty |
| `db2:supplier` | `COMP_ID` | char | Mã công ty |
