---
semantic_key: loyalty_tx_store_id
title: loyalty tx store id
display_names:
- STK_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: STK_ID
  type: char
- ref: db2:crdtrans
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
- 'db1:crdtrans_arc.STK_ID: top=10001(457), 10004(187), 10005(54)'
- 'db2:crdtrans.STK_ID: top=10001(589), 10004(233), 10005(178)'
---

# loyalty tx store id

**Semantic key:** `loyalty_tx_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Cột STK_ID trên CRDTRANS, CRDTRANS_ARC. db1:crdtrans_arc: top 10001; db2:crdtrans: top 10001.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:crdtrans` | `STK_ID` | char | Cửa hàng — sample 10001 |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:crdtrans.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

## Ghi chú thêm

- Mã cửa hàng / kho (10001, 10004, 10005, …)
