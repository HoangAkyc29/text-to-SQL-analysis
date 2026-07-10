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
- column_semantic_registry
- business_prose
---

# Mã khách trên header bill

**Semantic key:** `sale_customer_id` · **Cột vật lý:** `CUST_ID`

## Ý nghĩa nghiệp vụ

Mã khách trên header bill (TRANSHDR). Thường trống nếu KH không đăng ký; khác CUST_ID trên master loyalty CSCARD.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:transhdr` | `CUST_ID` | char | Mã khách hàng |

## Ghi chú thêm

- Mã khách hàng
