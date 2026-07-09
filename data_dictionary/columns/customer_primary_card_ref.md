---
semantic_key: customer_primary_card_ref
title: customer primary card ref
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db2:customer
  column: CARD_ID
  type: char
join_with:
- TRANS_NUM
- CUST_ID
related_semantic_keys: []
facts:
- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.CARD_ID: top=E10000002586(1), A10000075063(1), A10000051063(1), A10000040999(1),
  A10000067832(1)'
---

# customer primary card ref

**Semantic key:** `customer_primary_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Cột CARD_ID trên CUSTOMER. db2:customer: prefix EN (vd. E10000001281).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CARD_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `E10000001281`×1, `N10000000799`×1, `E10000000002`×1, `F10000000002`×1, `A10000044866`×1, `E10000000003`×1, `F10000000003`×1, `N10000000792`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
