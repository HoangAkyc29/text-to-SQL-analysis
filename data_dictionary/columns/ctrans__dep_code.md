---
semantic_key: ctrans__dep_code
title: Mã phân loại dep (CTRANS)
display_names:
- DEP_CODE
kind: code
tables:
- ref: db2:ctrans
  column: DEP_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- MãDEP_CODE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã phân loại dep (CTRANS)

**Semantic key:** `ctrans__dep_code` · **Cột vật lý:** `DEP_CODE`

## Ý nghĩa nghiệp vụ

Mã phòng ban / cost center trên dòng CTRANS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `DEP_CODE` | char | MãDEP_CODE |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- MãDEP_CODE
