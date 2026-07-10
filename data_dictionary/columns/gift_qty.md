---
semantic_key: gift_qty
title: gift qty
display_names:
- GIFT_QTY
- gift_qty
kind: measure
tables:
- ref: db1:strans
  column: GIFT_QTY
  type: numeric
- ref: db2:st_order
  column: GIFT_QTY
  type: decimal
- ref: db2:strans
  column: GIFT_QTY
  type: numeric
- ref: db2:strans_tmp
  column: GIFT_QTY
  type: numeric
- ref: db2:suspend
  column: GIFT_QTY
  type: decimal
- ref: db2:webrpt_sales_sku_daily
  column: gift_qty
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Số lượng quà tặng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# gift qty

**Semantic key:** `gift_qty` · **Cột vật lý:** `GIFT_QTY`, `gift_qty`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `GIFT_QTY` | numeric | Quà tặng: GIFT_QTY |
| `db2:st_order` | `GIFT_QTY` | decimal | Quà tặng: GIFT_QTY |
| `db2:strans` | `GIFT_QTY` | numeric | Quà tặng: GIFT_QTY |
| `db2:strans_tmp` | `GIFT_QTY` | numeric | Quà tặng: GIFT_QTY |
| `db2:suspend` | `GIFT_QTY` | decimal | Quà tặng: GIFT_QTY |
| `db2:webrpt_sales_sku_daily` | `gift_qty` | decimal | Số lượng quà tặng |

## Ghi chú thêm

- Số lượng quà tặng
