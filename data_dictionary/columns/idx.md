---
semantic_key: idx
title: idx
display_names:
- IDX
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: IDX
  type: numeric
- ref: db1:pmtrans
  column: IDX
  type: int
- ref: db1:strans
  column: IDX
  type: numeric
- ref: db1:transhdr_arc
  column: IDX
  type: numeric
- ref: db2:asso_inf
  column: IDX
  type: numeric
- ref: db2:crd_info
  column: IDX
  type: numeric
- ref: db2:crdtrans
  column: IDX
  type: numeric
- ref: db2:crdtrans_tmp
  column: IDX
  type: numeric
- ref: db2:cscard
  column: IDX
  type: int
- ref: db2:ctrans
  column: IDX
  type: int
- ref: db2:pmtrans
  column: IDX
  type: int
- ref: db2:rdiscinf
  column: IDX
  type: int
- ref: db2:st_order
  column: IDX
  type: numeric
- ref: db2:strans
  column: IDX
  type: numeric
- ref: db2:strans_tmp
  column: IDX
  type: numeric
- ref: db2:suspend
  column: IDX
  type: numeric
- ref: db2:transhdr
  column: IDX
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- ID nội bộ bản ghi tích lũy
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.IDX: top=0(1000)'
- 'db1:pmtrans.IDX: min=1.0 max=10.0'
- 'db1:strans.IDX: top=1(207), 2(143), 3(125), 4(82), 5(66)'
- 'db1:transhdr_arc.IDX: top=0(1000)'
- 'db2:asso_inf.IDX: top=1(512), 2(488)'
- 'db2:crd_info.IDX: top=0(1000)'
- 'db2:crdtrans.IDX: top=0(1000)'
- 'db2:crdtrans_tmp.IDX: top=0(1000)'
- 'db2:cscard.IDX: min=0.0 max=0.0'
- 'db2:ctrans.IDX: min=1.0 max=1.0'
- 'db2:pmtrans.IDX: min=1.0 max=9.0'
- 'db2:rdiscinf.IDX: min=0.0 max=120.0'
- 'db2:st_order.IDX: top=1(79), 2(75), 4(59), 3(58), 6(42)'
- 'db2:strans.IDX: top=1(190), 2(130), 3(121), 4(104), 5(71)'
- 'db2:strans_tmp.IDX: top=1(225), 2(171), 3(138), 4(104), 5(91)'
- 'db2:suspend.IDX: top=1(169), 2(137), 3(109), 4(103), 5(80)'
- 'db2:transhdr.IDX: top=0(1000)'
---

# idx

**Semantic key:** `idx` · **Cột vật lý:** `IDX`

## Ý nghĩa nghiệp vụ

Cột IDX trên ASSO_INF, CRDTRANS, CRDTRANS_ARC. db1:crdtrans_arc: top 0; db1:pmtrans: 1.0…2.0; db1:strans: top 1, 2, 3; db1:transhdr_arc: top 0; db2:asso_inf: top 1, 2; db2:crd_info: top 0; db2:crdtrans: top 0; db2:crdtrans_tmp: top 0; db2:cscard: 0.0…0.0; db2:ctrans: 1.0…1.0; db2:pmtrans: 1.0…1.0; db2:rdiscinf: 0.0…0.0; db2:st_order: top 1, 2, 3; db2:strans: top 1, 2, 3; db2:strans_tmp: top 1, 2, 3; db2:suspend: top 1, 2, 3; db2:transhdr: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `IDX` | numeric | có dữ liệu |
| `db1:pmtrans` | `IDX` | int | có dữ liệu |
| `db1:strans` | `IDX` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `IDX` | numeric | có dữ liệu |
| `db2:asso_inf` | `IDX` | numeric | có dữ liệu |
| `db2:crd_info` | `IDX` | numeric | có dữ liệu |
| `db2:crdtrans` | `IDX` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `IDX` | numeric | có dữ liệu |
| `db2:cscard` | `IDX` | int | có dữ liệu |
| `db2:ctrans` | `IDX` | int | có dữ liệu |
| `db2:pmtrans` | `IDX` | int | có dữ liệu |
| `db2:rdiscinf` | `IDX` | int | có dữ liệu |
| `db2:st_order` | `IDX` | numeric | có dữ liệu |
| `db2:strans` | `IDX` | numeric | có dữ liệu |
| `db2:strans_tmp` | `IDX` | numeric | có dữ liệu |
| `db2:suspend` | `IDX` | numeric | có dữ liệu |
| `db2:transhdr` | `IDX` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.IDX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db1:pmtrans.IDX`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 2.0
- Ví dụ: 1, 2, 1, 1, 2

### `db1:strans.IDX`
- Null rate trong sample: 0%
- Distinct ≈15; top: `1`×3, `2`×2, `3`×2, `4`×2, `5`×1, `6`×1, `7`×1, `8`×1

### `db1:transhdr_arc.IDX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:asso_inf.IDX`
- Null rate trong sample: 0%
- Distinct ≈2; top: `1`×10, `2`×10

### `db2:crd_info.IDX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:crdtrans.IDX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:crdtrans_tmp.IDX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:cscard.IDX`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:ctrans.IDX`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:pmtrans.IDX`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:rdiscinf.IDX`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:st_order.IDX`
- Null rate trong sample: 0%
- Distinct ≈17; top: `1`×2, `2`×2, `3`×2, `4`×1, `5`×1, `6`×1, `7`×1, `8`×1

### `db2:strans.IDX`
- Null rate trong sample: 0%
- Distinct ≈8; top: `1`×4, `2`×3, `3`×3, `4`×3, `5`×2, `6`×2, `7`×2, `8`×1

### `db2:strans_tmp.IDX`
- Null rate trong sample: 0%
- Distinct ≈7; top: `1`×6, `2`×5, `3`×3, `4`×2, `5`×2, `6`×1, `7`×1

### `db2:suspend.IDX`
- Null rate trong sample: 0%
- Distinct ≈13; top: `1`×2, `2`×2, `3`×2, `4`×2, `5`×2, `6`×2, `7`×2, `8`×1

### `db2:transhdr.IDX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- ID nội bộ bản ghi tích lũy
