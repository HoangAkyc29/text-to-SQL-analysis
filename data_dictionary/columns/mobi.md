---
semantic_key: mobi
title: mobi
display_names:
- MOBI
kind: text
tables:
- ref: db2:cscard
  column: MOBI
  type: varchar
- ref: db2:customer
  column: MOBI
  type: varchar
- ref: db2:partner
  column: MOBI
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Di động
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.MOBI: top=0934806608(1), 0778549337(1), 0961055111(1), 0967136194(1),
  0943629666(1)'
- 'db2:customer.MOBI: top=0943111444(1), 0935814803(1), 0943914270(1), 0829219806(1),
  0772561172(1)'
- 'db2:partner.MOBI: top=0913.404 419(1)'
---

# mobi

**Semantic key:** `mobi` · **Cột vật lý:** `MOBI`

## Ý nghĩa nghiệp vụ

Cột MOBI trên CSCARD, CUSTOMER, PARTNER. db2:cscard: top 0903203411; db2:customer: top 0914111553, 0905348048.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `MOBI` | varchar | có dữ liệu |
| `db2:customer` | `MOBI` | varchar | có dữ liệu |
| `db2:partner` | `MOBI` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.MOBI`
- Null rate trong sample: 95%
- Distinct ≈1; top: `0903203411`×1

### `db2:customer.MOBI`
- Null rate trong sample: 90%
- Distinct ≈2; top: `0914111553`×1, `0905348048`×1

## Ghi chú thêm

- Di động
