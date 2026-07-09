---
semantic_key: ostk_type
title: ostk type
display_names:
- OSTK_TYPE
kind: text
tables:
- ref: db1:strans
  column: OSTK_TYPE
  type: char
- ref: db2:st_order
  column: OSTK_TYPE
  type: char
- ref: db2:strans
  column: OSTK_TYPE
  type: char
- ref: db2:strans_tmp
  column: OSTK_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại kho đối ứng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.OSTK_TYPE: top=03(773), 05(53), 01(22), 06(2)'
- 'db2:st_order.OSTK_TYPE: top=01(1000)'
- 'db2:strans.OSTK_TYPE: top=03(871), 05(47), 01(10), 04(3), 06(1)'
- 'db2:strans_tmp.OSTK_TYPE: top=03(1000)'
---

# ostk type

**Semantic key:** `ostk_type` · **Cột vật lý:** `OSTK_TYPE`

## Ý nghĩa nghiệp vụ

Cột OSTK_TYPE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 05; db2:st_order: top 01; db2:strans: top 05; db2:strans_tmp: top 04.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `OSTK_TYPE` | char | có dữ liệu |
| `db2:st_order` | `OSTK_TYPE` | char | có dữ liệu |
| `db2:strans` | `OSTK_TYPE` | char | có dữ liệu |
| `db2:strans_tmp` | `OSTK_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.OSTK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

### `db2:st_order.OSTK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:strans.OSTK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

### `db2:strans_tmp.OSTK_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `04`×20

## Ghi chú thêm

- Loại kho đối ứng
