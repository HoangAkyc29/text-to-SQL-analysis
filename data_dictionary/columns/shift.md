---
semantic_key: shift
title: shift
display_names:
- SHIFT
kind: measure
tables:
- ref: db1:pmtrans
  column: SHIFT
  type: numeric
- ref: db1:strans
  column: SHIFT
  type: numeric
- ref: db1:transhdr_arc
  column: SHIFT
  type: numeric
- ref: db2:cash_st
  column: SHIFT
  type: numeric
- ref: db2:inv_iss
  column: SHIFT
  type: numeric
- ref: db2:pmtrans
  column: SHIFT
  type: numeric
- ref: db2:st_order
  column: SHIFT
  type: numeric
- ref: db2:strans
  column: SHIFT
  type: numeric
- ref: db2:strans_tmp
  column: SHIFT
  type: numeric
- ref: db2:suspend
  column: SHIFT
  type: numeric
- ref: db2:transhdr
  column: SHIFT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Ca làm việc
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.SHIFT: top=2(563), 1(436), 3(1)'
- 'db1:strans.SHIFT: top=2(414), 1(359), 0(227)'
- 'db1:transhdr_arc.SHIFT: top=2(502), 1(407), 0(62), 3(14), 5(5)'
- 'db2:cash_st.SHIFT: top=1(524), 2(458), 3(15), 4(2), 0(1)'
- 'db2:inv_iss.SHIFT: top=0(640), 1(227), 2(125), 3(7), 4(1)'
- 'db2:pmtrans.SHIFT: top=2(509), 1(484), 3(7)'
- 'db2:st_order.SHIFT: top=0(1000)'
- 'db2:strans.SHIFT: top=1(445), 2(419), 0(129), 3(7)'
- 'db2:strans_tmp.SHIFT: top=2(537), 1(453), 3(10)'
- 'db2:suspend.SHIFT: top=2(502), 1(426), 3(16), 4(13), 5(12)'
- 'db2:transhdr.SHIFT: top=1(480), 2(467), 0(48), 3(5)'
---

# shift

**Semantic key:** `shift` · **Cột vật lý:** `SHIFT`

## Ý nghĩa nghiệp vụ

Cột SHIFT trên CASH_ST, INV_ISS, PMTRANS. db1:pmtrans: top 1; db1:strans: top 0; db1:transhdr_arc: top 2; db2:cash_st: top 0, 2; db2:inv_iss: top 0; db2:pmtrans: top 1; db2:st_order: top 0; db2:strans: top 0; db2:strans_tmp: top 0; db2:suspend: top 2; db2:transhdr: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `SHIFT` | numeric | có dữ liệu |
| `db1:strans` | `SHIFT` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `SHIFT` | numeric | có dữ liệu |
| `db2:cash_st` | `SHIFT` | numeric | có dữ liệu |
| `db2:inv_iss` | `SHIFT` | numeric | có dữ liệu |
| `db2:pmtrans` | `SHIFT` | numeric | có dữ liệu |
| `db2:st_order` | `SHIFT` | numeric | có dữ liệu |
| `db2:strans` | `SHIFT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `SHIFT` | numeric | có dữ liệu |
| `db2:suspend` | `SHIFT` | numeric | có dữ liệu |
| `db2:transhdr` | `SHIFT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db1:strans.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db1:transhdr_arc.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2`×20

### `db2:cash_st.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0`×11, `2`×9

### `db2:inv_iss.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmtrans.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:st_order.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans_tmp.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:suspend.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2`×20

### `db2:transhdr.SHIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Ca làm việc
