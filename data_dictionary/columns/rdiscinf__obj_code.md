---
semantic_key: rdiscinf__obj_code
title: Mã phân loại obj (RDISCINF)
display_names:
- OBJ_CODE
kind: code
tables:
- ref: db2:rdiscinf
  column: OBJ_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- MãOBJ_CODE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã phân loại obj (RDISCINF)

**Semantic key:** `rdiscinf__obj_code` · **Cột vật lý:** `OBJ_CODE`

## Ý nghĩa nghiệp vụ

Mã đối tượng KM (SKU, ngành hàng, nhóm, …) — join với OBJ_VALUE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `OBJ_CODE` | char | MãOBJ_CODE |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- MãOBJ_CODE
