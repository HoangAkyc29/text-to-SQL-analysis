---
semantic_key: payment_store_id
title: Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)
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
- column_semantic_registry
- business_prose
---

# Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)

**Semantic key:** `payment_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Mã cửa hàng / kho (10001, 10004, 10005, …) (ngữ cảnh: dòng thanh toán / quỹ bill).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:pmtrans` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
