---
semantic_key: copies
title: copies
display_names:
- COPIES
kind: measure
tables:
- ref: db1:strans
  column: COPIES
  type: numeric
- ref: db1:transhdr_arc
  column: COPIES
  type: numeric
- ref: db2:inv_iss
  column: COPIES
  type: numeric
- ref: db2:st_order
  column: COPIES
  type: numeric
- ref: db2:strans
  column: COPIES
  type: numeric
- ref: db2:strans_tmp
  column: COPIES
  type: numeric
- ref: db2:transhdr
  column: COPIES
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột COPIES
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.COPIES: top=0(440), 1(280), 2(251), 3(21), 4(6)'
- 'db1:transhdr_arc.COPIES: top=0(1000)'
- 'db2:inv_iss.COPIES: top=0(1000)'
- 'db2:st_order.COPIES: top=0(1000)'
- 'db2:strans.COPIES: top=2(404), 1(378), 0(185), 3(27), 4(4)'
- 'db2:strans_tmp.COPIES: top=0(369), 1(325), 2(285), 3(14), 5(3)'
- 'db2:transhdr.COPIES: top=0(1000)'
---

# copies

**Semantic key:** `copies` · **Cột vật lý:** `COPIES`

## Ý nghĩa nghiệp vụ

Cột COPIES trên INV_ISS, STRANS, STRANS_TMP. db1:strans: top 1, 2; db1:transhdr_arc: top 0; db2:inv_iss: top 0; db2:st_order: top 0; db2:strans: top 1, 0; db2:strans_tmp: top 1, 2; db2:transhdr: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `COPIES` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `COPIES` | numeric | có dữ liệu |
| `db2:inv_iss` | `COPIES` | numeric | có dữ liệu |
| `db2:st_order` | `COPIES` | numeric | có dữ liệu |
| `db2:strans` | `COPIES` | numeric | có dữ liệu |
| `db2:strans_tmp` | `COPIES` | numeric | có dữ liệu |
| `db2:transhdr` | `COPIES` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.COPIES`
- Null rate trong sample: 0%
- Distinct ≈2; top: `1`×15, `2`×5

### `db1:transhdr_arc.COPIES`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:inv_iss.COPIES`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:st_order.COPIES`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.COPIES`
- Null rate trong sample: 0%
- Distinct ≈2; top: `1`×19, `0`×1

### `db2:strans_tmp.COPIES`
- Null rate trong sample: 0%
- Distinct ≈2; top: `1`×13, `2`×7

### `db2:transhdr.COPIES`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

