---
semantic_key: fax
title: fax
display_names:
- FAX
kind: text
tables:
- ref: db2:partner
  column: FAX
  type: varchar
- ref: db2:supplier
  column: FAX
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột FAX
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:partner.FAX: top=722266(1), 05113.739296(1), 0510722266(1), 045375985(1), 0511744622(1)'
- 'db2:supplier.FAX: top=08.38341208(1), 045375985(1), 05113.739296(1), 0510722266(1),
  0511 830 664(1)'
---

# fax

**Semantic key:** `fax` · **Cột vật lý:** `FAX`

## Ý nghĩa nghiệp vụ

Cột FAX trên PARTNER, SUPPLIER. db2:partner: top 087551837, 833208, 0510722266; db2:supplier: top 087551837, 833208, 0510722266.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `FAX` | varchar | có dữ liệu |
| `db2:supplier` | `FAX` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.FAX`
- Null rate trong sample: 85%
- Distinct ≈3; top: `087551837`×1, `833208`×1, `0510722266`×1

### `db2:supplier.FAX`
- Null rate trong sample: 85%
- Distinct ≈3; top: `087551837`×1, `833208`×1, `0510722266`×1

## Ghi chú thêm

