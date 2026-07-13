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

Tổng tiền cả bill trên `TRANSHDR.AMOUNT`. Khác grain với `AMOUNT` từng dòng `STRANS`. Công thức nghiệp vụ chi tiết (khi nào cộng `SURPLUS`/`VAT_AMT`, khi nào tin header) lấy từ **case study / column facts retrieve**, không hardcode một recipe duy nhất ở đây.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:transhdr` | `AMOUNT` | numeric | tổng tiền cả bill — dùng lọc bill tối thiểu (min bill) |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
