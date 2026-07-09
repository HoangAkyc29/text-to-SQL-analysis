---
semantic_key: payment_store_id
title: payment store id
display_names:
- STK_ID
kind: identifier
tables:
- ref: db1:pmtrans
  column: STK_ID
  type: char
- ref: db2:pmtrans
  column: STK_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã cửa hàng / kho (10001, 10004, 10005, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.STK_ID: top=10001(580), 10004(247), 10005(167)'
- 'db2:pmtrans.STK_ID: top=10001(516), 10004(246), 10005(224)'
---

# payment store id

**Semantic key:** `payment_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Cột STK_ID trên PMTRANS. db1:pmtrans: top 10004; db2:pmtrans: top 10001.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:pmtrans` | `STK_ID` | char | Cửa hàng — sample 10001 |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10004`×20

### `db2:pmtrans.STK_ID`
- Null rate trong sample: 15%
- Distinct ≈1; top: `10001`×17

## Ghi chú thêm

- Mã cửa hàng / kho (10001, 10004, 10005, …)
