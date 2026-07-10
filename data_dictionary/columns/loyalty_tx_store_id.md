---
semantic_key: loyalty_tx_store_id
title: Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)
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
- column_semantic_registry
- business_prose
---

# Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)

**Semantic key:** `loyalty_tx_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Mã cửa hàng / kho (10001, 10004, 10005, …). Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:crdtrans` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
