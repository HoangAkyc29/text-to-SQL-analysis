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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for AMOUNT
- 'db1:pmtrans.AMOUNT: top=500000.00(47), 50000.00(46), 200000.00(35), 100000.00(29),
  20000.00(16)'
- 'db2:pmtrans.AMOUNT: top=500000.00(56), 200000.00(38), 50000.00(32), 100000.00(30),
  20000.00(10)'
---

# Số tiền thanh toán PMTRANS

**Semantic key:** `amount_payment` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Số tiền trên PMTRANS — thanh toán bill. Sample có giá trị âm (chi quỹ/refund). TRANS_CODE 222/008 phổ biến trong sample.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `AMOUNT` | numeric | có dữ liệu |
| `db2:pmtrans` | `AMOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈19; top: `-400.00`×2, `200000.00`×1, `-91000.00`×1, `1687000.00`×1, `500000.00`×1, `-80374.00`×1, `105000.00`×1, `81500.00`×1

### `db2:pmtrans.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `-208560.00`×1, `-1071399.00`×1, `-1603186.00`×1, `-7000.00`×1, `-86000.00`×1, `-51500.00`×1, `-63000.00`×1, `-222900.00`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
