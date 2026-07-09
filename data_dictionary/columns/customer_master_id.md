---
semantic_key: customer_master_id
title: customer master id
display_names:
- CUST_ID
kind: identifier
tables:
- ref: db2:customer
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
evidence:
- 'db2:customer.CUST_ID: top=230000010115(1), 239010000536(1), 230000023720(1), 230000014509(1),
  239020000058(1)'
---

# customer master id

**Semantic key:** `customer_master_id` · **Cột vật lý:** `CUST_ID`

## Ý nghĩa nghiệp vụ

Cột CUST_ID trên CUSTOMER. db2:customer: top 230000000001, 230000000002, 230000000003.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CUST_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.CUST_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `230000000001`×1, `230000000002`×1, `230000000003`×1, `230000000004`×1, `230000000005`×1, `230000000006`×1, `230000000007`×1, `230000000008`×1

## Ghi chú thêm

- Mã khách hàng
