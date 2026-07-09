---
semantic_key: sale_customer_id
title: Mã khách trên header bill
display_names:
- CUST_ID
kind: identifier
tables:
- ref: db2:transhdr
  column: CUST_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã khách hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
---

# Mã khách trên header bill

**Semantic key:** `sale_customer_id` · **Cột vật lý:** `CUST_ID`

## Ý nghĩa nghiệp vụ

CUST_ID trên TRANSHDR — khách gắn bill. Sample thường rỗng nếu KH không đăng ký; khác CSCARD.CUST_ID (master loyalty).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:transhdr` | `CUST_ID` | char | Không có giá trị trong sample |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Mã khách hàng
