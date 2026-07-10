---
semantic_key: amount
title: Số tiền / giá trị giao dịch (grain phụ thuộc bảng) (AMOUNT)
display_names:
- Amount
- AMOUNT
kind: measure
tables:
- ref: db2:custhist
  column: AMOUNT
  type: numeric
- ref: db2:custsumm
  column: Amount
  type: numeric
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Tổng mua (CustSumm)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị giao dịch (grain phụ thuộc bảng) (AMOUNT)

**Semantic key:** `amount` · **Cột vật lý:** `Amount`, `AMOUNT`

## Ý nghĩa nghiệp vụ

Số tiền / giá trị — grain phụ thuộc bảng. TRANSHDR = tổng bill; STRANS = thành tiền dòng; PMTRANS = thanh toán; CRDTRANS = doanh thu tích điểm.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:custhist` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:custsumm` | `Amount` | numeric | Tổng mua (CustSumm) |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Tổng mua (CustSumm)
