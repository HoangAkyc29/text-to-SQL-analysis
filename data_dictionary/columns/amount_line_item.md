---
semantic_key: amount_line_item
title: Thành tiền / giá trị dòng hàng STRANS
display_names:
- AMOUNT
kind: measure
tables:
- ref: db1:strans
  column: AMOUNT
  type: numeric
- ref: db2:st_order
  column: AMOUNT
  type: decimal
- ref: db2:strans
  column: AMOUNT
  type: numeric
- ref: db2:strans_tmp
  column: AMOUNT
  type: numeric
- ref: db2:suspend
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

# Thành tiền / giá trị dòng hàng STRANS

**Semantic key:** `amount_line_item` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Thành tiền / giá trị trên dòng STRANS. Có thể bằng 0 với quà tặng hoặc khuyến mãi. Không thay TRANSHDR.AMOUNT khi lọc min bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `AMOUNT` | numeric | thành tiền từng dòng hàng — có thể bằng 0 với quà tặng |
| `db2:st_order` | `AMOUNT` | decimal | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:strans` | `AMOUNT` | numeric | thành tiền từng dòng hàng — có thể bằng 0 với quà tặng |
| `db2:strans_tmp` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:suspend` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
