---
semantic_key: tcomm_amt
title: tcomm amt
display_names:
- TCOMM_AMT
kind: measure
tables:
- ref: db1:strans
  column: TCOMM_AMT
  type: numeric
- ref: db2:st_order
  column: TCOMM_AMT
  type: numeric
- ref: db2:strans
  column: TCOMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: TCOMM_AMT
  type: numeric
- ref: db2:suspend
  column: TCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng transaction: TCOMM_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TCOMM_AMT: top=0.00(1000)'
- 'db2:st_order.TCOMM_AMT: top=0(1000)'
- 'db2:strans.TCOMM_AMT: top=0.00(1000)'
- 'db2:strans_tmp.TCOMM_AMT: top=0.00(1000)'
- 'db2:suspend.TCOMM_AMT: top=0.00(1000)'
---

# tcomm amt

**Semantic key:** `tcomm_amt` · **Cột vật lý:** `TCOMM_AMT`

## Ý nghĩa nghiệp vụ

Cột TCOMM_AMT trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TCOMM_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `TCOMM_AMT` | numeric | có dữ liệu |
| `db2:strans` | `TCOMM_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `TCOMM_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `TCOMM_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.TCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.TCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.TCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.TCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoa hồng transaction: TCOMM_AMT
