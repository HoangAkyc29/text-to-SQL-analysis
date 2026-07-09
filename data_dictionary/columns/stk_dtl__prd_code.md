---
semantic_key: stk_dtl__prd_code
title: stk dtl · prd code
display_names:
- PRD_CODE
kind: code
tables:
- ref: db2:stk_dtl
  column: PRD_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã kỳ tồn kho
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PRD_CODE
- 'db2:stk_dtl.PRD_CODE: top=202211(1000)'
---

# stk dtl · prd code

**Semantic key:** `stk_dtl__prd_code` · **Cột vật lý:** `PRD_CODE`

## Ý nghĩa nghiệp vụ

Cột PRD_CODE trên STK_DTL. db2:stk_dtl: top 202211.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `PRD_CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.PRD_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `202211`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã kỳ tồn kho
