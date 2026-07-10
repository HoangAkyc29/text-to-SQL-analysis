---
semantic_key: gcomm_qty
title: Số lượng quà / hàng KM trong combo (GCOMM_QTY)
display_names:
- GCOMM_QTY
kind: measure
tables:
- ref: db1:strans
  column: GCOMM_QTY
  type: numeric
- ref: db2:st_order
  column: GCOMM_QTY
  type: numeric
- ref: db2:strans
  column: GCOMM_QTY
  type: numeric
- ref: db2:strans_tmp
  column: GCOMM_QTY
  type: numeric
- ref: db2:suspend
  column: GCOMM_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng gift: GCOMM_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng quà / hàng KM trong combo (GCOMM_QTY)

**Semantic key:** `gcomm_qty` · **Cột vật lý:** `GCOMM_QTY`

## Ý nghĩa nghiệp vụ

Hoa hồng gift: GCOMM_QTY. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `GCOMM_QTY` | numeric | Hoa hồng gift: GCOMM_QTY |
| `db2:st_order` | `GCOMM_QTY` | numeric | Hoa hồng gift: GCOMM_QTY |
| `db2:strans` | `GCOMM_QTY` | numeric | Hoa hồng gift: GCOMM_QTY |
| `db2:strans_tmp` | `GCOMM_QTY` | numeric | Hoa hồng gift: GCOMM_QTY |
| `db2:suspend` | `GCOMM_QTY` | numeric | Hoa hồng gift: GCOMM_QTY |
