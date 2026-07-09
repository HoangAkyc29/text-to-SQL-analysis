---
semantic_key: loyalty_card_customer_id
title: loyalty card customer id
display_names:
- CUST_ID
kind: identifier
tables:
- ref: db2:cscard
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
- 'db2:cscard.CUST_ID: top=239010005449(1), 230000019975(1), 239010000672(1), 230000030326(1),
  230000009176(1)'
---

# loyalty card customer id

**Semantic key:** `loyalty_card_customer_id` · **Cột vật lý:** `CUST_ID`

## Ý nghĩa nghiệp vụ

Cột CUST_ID trên CSCARD. db2:cscard: top 230000001980, 230000012780, 230000012781.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `CUST_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.CUST_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `230000001980`×1, `230000012780`×1, `230000012781`×1, `230000000061`×1, `230000012782`×1, `230000012783`×1, `230000012784`×1, `230000012785`×1

## Ghi chú thêm

- Mã khách hàng
