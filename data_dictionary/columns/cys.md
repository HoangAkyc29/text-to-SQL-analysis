---
semantic_key: cys
title: cys
display_names:
- CYS
kind: text
tables:
- ref: db1:pmtrans
  column: CYS
  type: char
- ref: db2:account
  column: CYS
  type: char
- ref: db2:cash_st
  column: CYS
  type: char
- ref: db2:ctrans
  column: CYS
  type: char
- ref: db2:debt
  column: CYS
  type: char
- ref: db2:pmtrans
  column: CYS
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại tiền (VND)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.CYS: top=VND(1000)'
- 'db2:account.CYS: top=VND(1000)'
- 'db2:cash_st.CYS: top=VND(1000)'
- 'db2:ctrans.CYS: top=VND(1000)'
- 'db2:debt.CYS: top=VND(1000)'
- 'db2:pmtrans.CYS: top=VND(1000)'
---

# cys

**Semantic key:** `cys` · **Cột vật lý:** `CYS`

## Ý nghĩa nghiệp vụ

Cột CYS trên ACCOUNT, CASH_ST, CTRANS. db1:pmtrans: top VND; db2:account: top VND; db2:cash_st: top VND; db2:ctrans: top VND; db2:debt: top VND; db2:pmtrans: top VND.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `CYS` | char | có dữ liệu |
| `db2:account` | `CYS` | char | có dữ liệu |
| `db2:cash_st` | `CYS` | char | có dữ liệu |
| `db2:ctrans` | `CYS` | char | có dữ liệu |
| `db2:debt` | `CYS` | char | có dữ liệu |
| `db2:pmtrans` | `CYS` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

### `db2:account.CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

### `db2:cash_st.CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

### `db2:ctrans.CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

### `db2:debt.CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

### `db2:pmtrans.CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

## Ghi chú thêm

- Loại tiền (VND)
