---
semantic_key: sale_store_id
title: Cửa hàng phát sinh dòng bán (STRANS.STK_ID)
display_names:
- STK_ID
kind: identifier
tables:
- ref: db1:strans
  column: STK_ID
  type: char
- ref: db2:strans
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
- 'db1:strans.STK_ID: top=10001(567), 10004(274), 10005(156), 20001(2), 20002(1)'
- 'db2:strans.STK_ID: top=10001(578), 10004(219), 10005(199), 20002(4)'
---

# Cửa hàng phát sinh dòng bán (STRANS.STK_ID)

**Semantic key:** `sale_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Cột STK_ID trên STRANS. db1:strans: top 10001; db2:strans: top 10005, 10001.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:strans` | `STK_ID` | char | Cửa hàng — sample 10001 |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:strans.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `10005`×15, `10001`×5

## Ghi chú thêm

- Mã cửa hàng / kho (10001, 10004, 10005, …)
