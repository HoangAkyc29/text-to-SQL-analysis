---
semantic_key: mcomm_amt
title: mcomm amt
display_names:
- MCOMM_AMT
kind: measure
tables:
- ref: db1:strans
  column: MCOMM_AMT
  type: numeric
- ref: db2:st_order
  column: MCOMM_AMT
  type: numeric
- ref: db2:strans
  column: MCOMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: MCOMM_AMT
  type: numeric
- ref: db2:suspend
  column: MCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng manual: MCOMM_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MCOMM_AMT: top=0.00(1000)'
- 'db2:st_order.MCOMM_AMT: top=0(1000)'
- 'db2:strans.MCOMM_AMT: top=0.00(1000)'
- 'db2:strans_tmp.MCOMM_AMT: top=0.00(1000)'
- 'db2:suspend.MCOMM_AMT: top=0.00(1000)'
---

# mcomm amt

**Semantic key:** `mcomm_amt` · **Cột vật lý:** `MCOMM_AMT`

## Ý nghĩa nghiệp vụ

Cột MCOMM_AMT trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MCOMM_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `MCOMM_AMT` | numeric | có dữ liệu |
| `db2:strans` | `MCOMM_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `MCOMM_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `MCOMM_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.MCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.MCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.MCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.MCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.MCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoa hồng manual: MCOMM_AMT
