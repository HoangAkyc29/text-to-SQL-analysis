---
semantic_key: district
title: district
display_names:
- DISTRICT
kind: text
tables:
- ref: db2:cscard
  column: DISTRICT
  type: nvarchar
- ref: db2:customer
  column: DISTRICT
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột DISTRICT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.DISTRICT: top=Quan Hai Chau(108), Quan 1(40), Quan Thanh Khe(5), Quan
  Son Tra(5), Quan Lien Chieu(2)'
- 'db2:customer.DISTRICT: top=Quan Hai Chau(98), Quan 1(55), Quan Thanh Khe(8), Quan
  Son Tra(6), Huyen Hoa Vang(2)'
---

# district

**Semantic key:** `district` · **Cột vật lý:** `DISTRICT`

## Ý nghĩa nghiệp vụ

Cột DISTRICT trên CSCARD, CUSTOMER. db2:cscard: top Quan 1.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `DISTRICT` | nvarchar | có dữ liệu |
| `db2:customer` | `DISTRICT` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.DISTRICT`
- Null rate trong sample: 95%
- Distinct ≈1; top: `Quan 1`×1

## Ghi chú thêm

