---
semantic_key: comm_rate
title: comm rate
display_names:
- COMM_RATE
kind: measure
tables:
- ref: db1:strans
  column: COMM_RATE
  type: numeric
- ref: db2:customer
  column: COMM_RATE
  type: numeric
- ref: db2:st_order
  column: COMM_RATE
  type: decimal
- ref: db2:strans
  column: COMM_RATE
  type: numeric
- ref: db2:strans_tmp
  column: COMM_RATE
  type: numeric
- ref: db2:supplier
  column: COMM_RATE
  type: numeric
- ref: db2:suspend
  column: COMM_RATE
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệ hoa hồng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.COMM_RATE: top=0.00(1000)'
- 'db2:customer.COMM_RATE: top=0.00(1000)'
- 'db2:st_order.COMM_RATE: top=0.00(1000)'
- 'db2:strans.COMM_RATE: top=0.00(1000)'
- 'db2:strans_tmp.COMM_RATE: top=0.00(1000)'
- 'db2:supplier.COMM_RATE: top=0.00(1000)'
- 'db2:suspend.COMM_RATE: top=0.00(1000)'
---

# comm rate

**Semantic key:** `comm_rate` · **Cột vật lý:** `COMM_RATE`

## Ý nghĩa nghiệp vụ

Cột COMM_RATE trên CUSTOMER, STRANS, STRANS_TMP. db1:strans: top 0.00; db2:customer: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:supplier: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `COMM_RATE` | numeric | có dữ liệu |
| `db2:customer` | `COMM_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `COMM_RATE` | decimal | có dữ liệu |
| `db2:strans` | `COMM_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `COMM_RATE` | numeric | có dữ liệu |
| `db2:supplier` | `COMM_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `COMM_RATE` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:customer.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:supplier.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.COMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tỷ lệ hoa hồng
