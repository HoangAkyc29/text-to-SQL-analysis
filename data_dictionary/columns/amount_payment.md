---
semantic_key: amount_payment
title: Số tiền thanh toán PMTRANS
display_names:
- AMOUNT
kind: measure
tables:
- ref: db1:pmtrans
  column: AMOUNT
  type: numeric
- ref: db2:pmtrans
  column: AMOUNT
  type: numeric
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Thành tiền / số tiền (ngữ cảnh theo bảng)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền thanh toán PMTRANS

**Semantic key:** `amount_payment` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Số tiền trên PMTRANS — thanh toán hoặc chi quỹ bill. Có thể âm khi hoàn / điều chỉnh quỹ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `AMOUNT` | numeric | số tiền thanh toán / chi quỹ trên bill |
| `db2:pmtrans` | `AMOUNT` | numeric | số tiền thanh toán / chi quỹ trên bill |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
