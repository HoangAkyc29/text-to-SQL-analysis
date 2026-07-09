---
semantic_key: tdadd_amt
title: tdadd amt
display_names:
- TDADD_AMT
kind: measure
tables:
- ref: db1:strans
  column: TDADD_AMT
  type: numeric
- ref: db2:st_order
  column: TDADD_AMT
  type: numeric
- ref: db2:strans
  column: TDADD_AMT
  type: numeric
- ref: db2:strans_tmp
  column: TDADD_AMT
  type: numeric
- ref: db2:suspend
  column: TDADD_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu transaction: TDADD_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TDADD_AMT: top=0.00(1000)'
- 'db2:st_order.TDADD_AMT: top=0.00(1000)'
- 'db2:strans.TDADD_AMT: top=0.00(1000)'
- 'db2:strans_tmp.TDADD_AMT: top=0.00(1000)'
- 'db2:suspend.TDADD_AMT: top=0.00(1000)'
---

# tdadd amt

**Semantic key:** `tdadd_amt` · **Cột vật lý:** `TDADD_AMT`

## Ý nghĩa nghiệp vụ

Cột TDADD_AMT trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TDADD_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `TDADD_AMT` | numeric | có dữ liệu |
| `db2:strans` | `TDADD_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `TDADD_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `TDADD_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TDADD_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.TDADD_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.TDADD_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.TDADD_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.TDADD_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Phụ thu transaction: TDADD_AMT
