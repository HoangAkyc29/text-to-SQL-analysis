---
semantic_key: customer__cust_code
title: customer · cust code
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CUST_CODE
- 'db2:customer.CUST_CODE: top=230000010115(1), 239010000536(1), 239020000058(1),
  239010004133(1), 230000008142(1)'
---

# customer · cust code

**Semantic key:** `customer__cust_code` · **Cột vật lý:** `CUST_CODE`

## Ý nghĩa nghiệp vụ

Mã khách (hiển thị)

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CUST_CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

