---
semantic_key: sale_header_store_id
title: Cửa hàng trên header bill
display_names:
- STK_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: STK_ID
  type: char
- ref: db2:transhdr
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
---

# Cửa hàng trên header bill

**Semantic key:** `sale_header_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Mã cửa hàng / kho (10001, 10004, 10005, …)

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:transhdr` | `STK_ID` | char | Cửa hàng — sample 10001 |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

