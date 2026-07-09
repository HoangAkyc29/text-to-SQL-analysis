---
semantic_key: pos_id
title: pos id
display_names:
- POS_ID
kind: identifier
tables:
- ref: db1:pmtrans
  column: POS_ID
  type: int
- ref: db2:cash_st
  column: POS_ID
  type: int
- ref: db2:pmtrans
  column: POS_ID
  type: int
join_with: []
related_semantic_keys: []
facts:
- Mã quầy POS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.POS_ID: min=2.0 max=44.0'
- 'db2:cash_st.POS_ID: min=1.0 max=44.0'
- 'db2:pmtrans.POS_ID: min=2.0 max=44.0'
---

# pos id

**Semantic key:** `pos_id` · **Cột vật lý:** `POS_ID`

## Ý nghĩa nghiệp vụ

Cột POS_ID trên CASH_ST, PMTRANS. db1:pmtrans: 23.0…23.0; db2:cash_st: 1.0…1.0; db2:pmtrans: 2.0…2.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `POS_ID` | int | có dữ liệu |
| `db2:cash_st` | `POS_ID` | int | có dữ liệu |
| `db2:pmtrans` | `POS_ID` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.POS_ID`
- Null rate trong sample: 0%
- Numeric range: 23.0 … 23.0
- Ví dụ: 23, 23, 23, 23, 23

### `db2:cash_st.POS_ID`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:pmtrans.POS_ID`
- Null rate trong sample: 0%
- Numeric range: 2.0 … 2.0
- Ví dụ: 2, 2, 2, 2, 2

## Ghi chú thêm

- Mã quầy POS
