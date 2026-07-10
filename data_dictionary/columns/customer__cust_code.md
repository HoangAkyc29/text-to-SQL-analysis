---
semantic_key: customer__cust_code
title: Mã khách hiển thị / mã tra cứu (CUSTOMER)
display_names:
- CUST_CODE
kind: code
tables:
- ref: db2:customer
  column: CUST_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã khách (hiển thị)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã khách hiển thị / mã tra cứu (CUSTOMER)

**Semantic key:** `customer__cust_code` · **Cột vật lý:** `CUST_CODE`

## Ý nghĩa nghiệp vụ

Mã khách hiển thị / mã tra cứu — danh mục master khách hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `CUST_CODE` | varchar | Mã khách (hiển thị) |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã khách (hiển thị)
