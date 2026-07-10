---
semantic_key: qty
title: Số lượng (QTY)
display_names:
- qty
- QTY
kind: measure
tables:
- ref: db2:asso_inf
  column: QTY
  type: numeric
- ref: db2:cash_st
  column: QTY
  type: numeric
- ref: db2:custhist
  column: QTY
  type: numeric
- ref: db2:st_order
  column: QTY
  type: numeric
- ref: db2:strans_tmp
  column: QTY
  type: numeric
- ref: db2:suspend
  column: QTY
  type: numeric
- ref: db2:webrpt_sales_sku_daily
  column: qty
  type: decimal
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Số lượng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (QTY)

**Semantic key:** `qty` · **Cột vật lý:** `qty`, `QTY`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `QTY` | numeric | Số lượng trên chi tiết thành phần combo |
| `db2:cash_st` | `QTY` | numeric | Số tờ theo mệnh giá trong ca |
| `db2:custhist` | `QTY` | numeric | Số lượng trên lịch sử thay đổi thông tin khách |
| `db2:st_order` | `QTY` | numeric | Số lượng trên đơn đặt hàng nội bộ |
| `db2:strans_tmp` | `QTY` | numeric | Số lượng trên dòng bán tạm / suspend |
| `db2:suspend` | `QTY` | numeric | Số lượng trên bill đang treo / chưa hoàn tất |
| `db2:webrpt_sales_sku_daily` | `qty` | decimal | Số lượng bán trong ngày |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`
