---
semantic_key: payment_method_code
title: 'Hình thức TT: CASH, CARD, BANK'
display_names:
- PMT_CODE
kind: code
tables:
- ref: db1:pmtrans
  column: PMT_CODE
  type: char
- ref: db2:pmtrans
  column: PMT_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- 'Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space)'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Hình thức TT: CASH, CARD, BANK

**Semantic key:** `payment_method_code` · **Cột vật lý:** `PMT_CODE`

## Ý nghĩa nghiệp vụ

Hình thức thanh toán trên PMTRANS: tiền mặt (CASH), thẻ (CARD), chuyển khoản (BANK), …

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `PMT_CODE` | char | Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space) |
| `db2:pmtrans` | `PMT_CODE` | char | Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space) |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space)
