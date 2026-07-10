---
semantic_key: rtprice
title: Giá bán lẻ đề xuất (RTPRICE)
display_names:
- RTPRICE
kind: measure
tables:
- ref: db2:asso_inf
  column: RTPRICE
  type: numeric
- ref: db2:hisrtpr
  column: RTPRICE
  type: numeric
- ref: db2:plu
  column: RTPRICE
  type: numeric
- ref: db2:sku_def
  column: RTPRICE
  type: numeric
- ref: db2:st_order
  column: RTPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá bán lẻ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giá bán lẻ đề xuất (RTPRICE)

**Semantic key:** `rtprice` · **Cột vật lý:** `RTPRICE`

## Ý nghĩa nghiệp vụ

Giá bán lẻ. Dùng trong Kho / mua hàng (ST_ORDER); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `RTPRICE` | numeric | Giá bán lẻ |
| `db2:hisrtpr` | `RTPRICE` | numeric | Giá bán lẻ |
| `db2:plu` | `RTPRICE` | numeric | Giá bán lẻ |
| `db2:sku_def` | `RTPRICE` | numeric | Giá bán lẻ |
| `db2:st_order` | `RTPRICE` | numeric | Giá bán lẻ |
