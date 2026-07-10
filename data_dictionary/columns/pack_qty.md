---
semantic_key: pack_qty
title: Số lượng trong pack / thùng (PACK_QTY)
display_names:
- PACK_QTY
kind: measure
tables:
- ref: db1:strans
  column: PACK_QTY
  type: numeric
- ref: db2:strans
  column: PACK_QTY
  type: numeric
- ref: db2:strans_tmp
  column: PACK_QTY
  type: numeric
- ref: db2:suspend
  column: PACK_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng gói
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng trong pack / thùng (PACK_QTY)

**Semantic key:** `pack_qty` · **Cột vật lý:** `PACK_QTY`

## Ý nghĩa nghiệp vụ

Số lượng gói. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `PACK_QTY` | numeric | Số lượng gói |
| `db2:strans` | `PACK_QTY` | numeric | Số lượng gói |
| `db2:strans_tmp` | `PACK_QTY` | numeric | Số lượng gói |
| `db2:suspend` | `PACK_QTY` | numeric | Số lượng gói |
