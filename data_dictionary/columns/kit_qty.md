---
semantic_key: kit_qty
title: Số lượng trong kit (KIT_QTY)
display_names:
- KIT_QTY
kind: measure
tables:
- ref: db1:strans
  column: KIT_QTY
  type: numeric
- ref: db2:st_order
  column: KIT_QTY
  type: numeric
- ref: db2:strans
  column: KIT_QTY
  type: numeric
- ref: db2:strans_tmp
  column: KIT_QTY
  type: numeric
- ref: db2:suspend
  column: KIT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng kit
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng trong kit (KIT_QTY)

**Semantic key:** `kit_qty` · **Cột vật lý:** `KIT_QTY`

## Ý nghĩa nghiệp vụ

Số lượng kit. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `KIT_QTY` | numeric | Số lượng kit |
| `db2:st_order` | `KIT_QTY` | numeric | Số lượng kit |
| `db2:strans` | `KIT_QTY` | numeric | Số lượng kit |
| `db2:strans_tmp` | `KIT_QTY` | numeric | Số lượng kit |
| `db2:suspend` | `KIT_QTY` | numeric | Số lượng kit |
