---
semantic_key: own_compid
title: own compid
display_names:
- OWN_COMPID
kind: text
tables:
- ref: db2:customer
  column: OWN_COMPID
  type: char
- ref: db2:supplier
  column: OWN_COMPID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột OWN_COMPID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.OWN_COMPID: top=00(519)'
- 'db2:supplier.OWN_COMPID: top=00(374)'
---

# own compid

**Semantic key:** `own_compid` · **Cột vật lý:** `OWN_COMPID`

## Ý nghĩa nghiệp vụ

Cột OWN_COMPID trên CUSTOMER, SUPPLIER. db2:supplier: top 00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `OWN_COMPID` | char | có dữ liệu |
| `db2:supplier` | `OWN_COMPID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.OWN_COMPID`
- Null rate trong sample: 90%
- Distinct ≈1; top: `00`×2

## Ghi chú thêm

