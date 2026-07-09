---
semantic_key: ctrans__dep_code
title: ctrans · dep code
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DEP_CODE
- 'db2:ctrans.DEP_CODE: top=K(1000)'
---

# ctrans · dep code

**Semantic key:** `ctrans__dep_code` · **Cột vật lý:** `DEP_CODE`

## Ý nghĩa nghiệp vụ

Cột DEP_CODE trên CTRANS. db2:ctrans: top K.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `DEP_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.DEP_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `K`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- MãDEP_CODE
