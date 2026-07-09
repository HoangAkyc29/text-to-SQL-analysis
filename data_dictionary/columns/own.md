---
semantic_key: own
title: own
display_names:
- OWN
kind: flag
tables:
- ref: db2:customer
  column: OWN
  type: bit
- ref: db2:inv_hdr
  column: OWN
  type: bit
- ref: db2:partner
  column: OWN
  type: bit
- ref: db2:supplier
  column: OWN
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột OWN
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.OWN: top=False(997), True(3)'
- 'db2:inv_hdr.OWN: top=False(984), True(16)'
- 'db2:partner.OWN: top=False(999), True(1)'
- 'db2:supplier.OWN: top=False(999), True(1)'
---

# own

**Semantic key:** `own` · **Cột vật lý:** `OWN`

## Ý nghĩa nghiệp vụ

Cột OWN trên CUSTOMER, INV_HDR, PARTNER. db2:customer: top False; db2:inv_hdr: top False; db2:partner: top False; db2:supplier: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `OWN` | bit | có dữ liệu |
| `db2:inv_hdr` | `OWN` | bit | có dữ liệu |
| `db2:partner` | `OWN` | bit | có dữ liệu |
| `db2:supplier` | `OWN` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.OWN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:inv_hdr.OWN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:partner.OWN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:supplier.OWN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

