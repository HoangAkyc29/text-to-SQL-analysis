---
semantic_key: company
title: company
display_names:
- COMPANY
kind: flag
tables:
- ref: db2:customer
  column: COMPANY
  type: bit
- ref: db2:inv_iss
  column: COMPANY
  type: bit
- ref: db2:partner
  column: COMPANY
  type: bit
- ref: db2:supplier
  column: COMPANY
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột COMPANY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.COMPANY: top=False(999), True(1)'
- 'db2:inv_iss.COMPANY: top=False(999), True(1)'
- 'db2:partner.COMPANY: top=False(1000)'
- 'db2:supplier.COMPANY: top=False(1000)'
---

# company

**Semantic key:** `company` · **Cột vật lý:** `COMPANY`

## Ý nghĩa nghiệp vụ

Cột COMPANY trên CUSTOMER, INV_ISS, PARTNER. db2:customer: top False; db2:inv_iss: top False; db2:partner: top False; db2:supplier: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `COMPANY` | bit | có dữ liệu |
| `db2:inv_iss` | `COMPANY` | bit | có dữ liệu |
| `db2:partner` | `COMPANY` | bit | có dữ liệu |
| `db2:supplier` | `COMPANY` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.COMPANY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:inv_iss.COMPANY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:partner.COMPANY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:supplier.COMPANY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

