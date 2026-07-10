---
semantic_key: gift_sqty
title: Số lượng quà tặng (GIFT_SQTY)
display_names:
- GIFT_SQTY
kind: measure
tables:
- ref: db1:strans
  column: GIFT_SQTY
  type: numeric
- ref: db2:st_order
  column: GIFT_SQTY
  type: decimal
- ref: db2:strans
  column: GIFT_SQTY
  type: numeric
- ref: db2:strans_tmp
  column: GIFT_SQTY
  type: numeric
- ref: db2:suspend
  column: GIFT_SQTY
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- 'Quà tặng: GIFT_SQTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng quà tặng (GIFT_SQTY)

**Semantic key:** `gift_sqty` · **Cột vật lý:** `GIFT_SQTY`

## Ý nghĩa nghiệp vụ

Quà tặng: GIFT_SQTY. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `GIFT_SQTY` | numeric | Quà tặng: GIFT_SQTY |
| `db2:st_order` | `GIFT_SQTY` | decimal | Quà tặng: GIFT_SQTY |
| `db2:strans` | `GIFT_SQTY` | numeric | Quà tặng: GIFT_SQTY |
| `db2:strans_tmp` | `GIFT_SQTY` | numeric | Quà tặng: GIFT_SQTY |
| `db2:suspend` | `GIFT_SQTY` | decimal | Quà tặng: GIFT_SQTY |
