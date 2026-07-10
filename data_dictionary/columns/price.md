---
semantic_key: price
title: Đơn giá bán (PRICE)
display_names:
- PRICE
kind: measure
tables:
- ref: db2:asso_inf
  column: PRICE
  type: numeric
- ref: db2:st_order
  column: PRICE
  type: decimal
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Đơn giá
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Đơn giá bán (PRICE)

**Semantic key:** `price` · **Cột vật lý:** `PRICE`

## Ý nghĩa nghiệp vụ

Đơn giá bán trên dòng POS (STRANS). Khác RTPRICE trên master SKU — PRICE là giá thực tế tại thời điểm bán.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `PRICE` | numeric | Đơn giá bán trên chi tiết thành phần combo |
| `db2:st_order` | `PRICE` | decimal | Đơn giá bán trên đơn đặt hàng nội bộ |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`
