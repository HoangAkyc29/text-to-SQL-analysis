---
semantic_key: amount_debt_entry
title: Số tiền / giá trị giao dịch (grain phụ thuộc bảng) (AMOUNT)
display_names:
- AMOUNT
kind: measure
tables:
- ref: db2:ctrans
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

# Số tiền / giá trị giao dịch (grain phụ thuộc bảng) (AMOUNT)

**Semantic key:** `amount_debt_entry` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Số tiền / giá trị — grain phụ thuộc bảng. TRANSHDR = tổng bill; STRANS = thành tiền dòng; PMTRANS = thanh toán; CRDTRANS = doanh thu tích điểm. Chỉ xuất hiện trên chứng từ kế toán / công nợ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
