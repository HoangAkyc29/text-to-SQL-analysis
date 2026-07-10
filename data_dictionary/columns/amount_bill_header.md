---
semantic_key: amount_bill_header
title: Tổng tiền bill header — lọc min bill
display_names:
- AMOUNT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: AMOUNT
  type: numeric
- ref: db2:transhdr
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

# Tổng tiền bill header — lọc min bill

**Semantic key:** `amount_bill_header` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Tổng tiền cả bill trên TRANSHDR (TRANS_CODE=113). Dùng cho điều kiện bill tối thiểu (min bill). Khác grain với AMOUNT từng dòng STRANS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:transhdr` | `AMOUNT` | numeric | tổng tiền cả bill — dùng lọc bill tối thiểu (min bill) |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
