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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.PMT_CODE: top=CASH(682), BANK(197), CARD(84), OWNCP(36), DEBT(1)'
- 'db2:pmtrans.PMT_CODE: top=CASH(667), BANK(238), CARD(77), OWNCP(18)'
---

# Hình thức TT: CASH, CARD, BANK

**Semantic key:** `payment_method_code` · **Cột vật lý:** `PMT_CODE`

## Ý nghĩa nghiệp vụ

PMT_CODE trên PMTRANS: CASH, CARD, BANK. Phân biệt hình thức thanh toán trong bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `PMT_CODE` | char | có dữ liệu |
| `db2:pmtrans` | `PMT_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.PMT_CODE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `CASH`×15, `BANK`×3, `CARD`×2

### `db2:pmtrans.PMT_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `CASH`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space)
