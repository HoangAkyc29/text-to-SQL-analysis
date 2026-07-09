---
semantic_key: city
title: city
display_names:
- CITY
kind: text
tables:
- ref: db2:cscard
  column: CITY
  type: nvarchar
- ref: db2:customer
  column: CITY
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột CITY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.CITY: top=Da Nang(236), Ho Chi Minh(105), Thanh Hoa(1)'
- 'db2:customer.CITY: top=Da Nang(220), Ho Chi Minh(119), Quang Nam(2), da nang(1)'
---

# city

**Semantic key:** `city` · **Cột vật lý:** `CITY`

## Ý nghĩa nghiệp vụ

Cột CITY trên CSCARD, CUSTOMER. db2:cscard: top Ho Chi Minh.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `CITY` | nvarchar | có dữ liệu |
| `db2:customer` | `CITY` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.CITY`
- Null rate trong sample: 95%
- Distinct ≈1; top: `Ho Chi Minh`×1

## Ghi chú thêm

