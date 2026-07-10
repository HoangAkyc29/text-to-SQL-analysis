---
semantic_key: pmt_code
title: Hình thức thanh toán (tiền mặt, thẻ, chuyển khoản, …) (PMT_CODE)
display_names:
- PMT_CODE
kind: code
tables:
- ref: db2:cash_st
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

# Hình thức thanh toán (tiền mặt, thẻ, chuyển khoản, …) (PMT_CODE)

**Semantic key:** `pmt_code` · **Cột vật lý:** `PMT_CODE`

## Ý nghĩa nghiệp vụ

Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space) (ngữ cảnh: quỹ tiền mặt theo mệnh giá).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cash_st` | `PMT_CODE` | char | Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space) |

## Join

Thường join: `TRANS_NUM`
