---
semantic_key: cnt_qty
title: Số lượng đếm / count quantity (CNT_QTY)
display_names:
- CNT_QTY
kind: measure
tables:
- ref: db1:strans
  column: CNT_QTY
  type: numeric
- ref: db2:strans
  column: CNT_QTY
  type: numeric
- ref: db2:strans_tmp
  column: CNT_QTY
  type: numeric
- ref: db2:suspend
  column: CNT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngCNT_QTY
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng đếm / count quantity (CNT_QTY)

**Semantic key:** `cnt_qty` · **Cột vật lý:** `CNT_QTY`

## Ý nghĩa nghiệp vụ

Số lượngCNT_QTY. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `CNT_QTY` | numeric | Số lượngCNT_QTY |
| `db2:strans` | `CNT_QTY` | numeric | Số lượngCNT_QTY |
| `db2:strans_tmp` | `CNT_QTY` | numeric | Số lượngCNT_QTY |
| `db2:suspend` | `CNT_QTY` | numeric | Số lượngCNT_QTY |
