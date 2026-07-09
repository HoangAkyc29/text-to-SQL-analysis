---
semantic_key: stk_type
title: stk type
display_names:
- STK_TYPE
kind: text
tables:
- ref: db1:strans
  column: STK_TYPE
  type: char
- ref: db2:st_order
  column: STK_TYPE
  type: char
- ref: db2:strans
  column: STK_TYPE
  type: char
- ref: db2:strans_tmp
  column: STK_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại kho
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.STK_TYPE: top=01(1000)'
- 'db2:st_order.STK_TYPE: top=01(1000)'
- 'db2:strans.STK_TYPE: top=01(997), 02(3)'
- 'db2:strans_tmp.STK_TYPE: top=01(1000)'
---

# stk type

**Semantic key:** `stk_type` · **Cột vật lý:** `STK_TYPE`

## Ý nghĩa nghiệp vụ

Cột STK_TYPE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 01; db2:st_order: top 01; db2:strans: top 01; db2:strans_tmp: top 01, 02.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `STK_TYPE` | char | có dữ liệu |
| `db2:st_order` | `STK_TYPE` | char | có dữ liệu |
| `db2:strans` | `STK_TYPE` | char | có dữ liệu |
| `db2:strans_tmp` | `STK_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.STK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:st_order.STK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:strans.STK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:strans_tmp.STK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `01`×13, `02`×7

## Ghi chú thêm

- Loại kho
