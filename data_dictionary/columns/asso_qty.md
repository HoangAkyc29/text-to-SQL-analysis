---
semantic_key: asso_qty
title: Số lượng trong combo (ASSO_QTY)
display_names:
- ASSO_QTY
kind: measure
tables:
- ref: db1:strans
  column: ASSO_QTY
  type: numeric
- ref: db2:strans
  column: ASSO_QTY
  type: numeric
- ref: db2:strans_tmp
  column: ASSO_QTY
  type: numeric
- ref: db2:suspend
  column: ASSO_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng trong combo
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng trong combo (ASSO_QTY)

**Semantic key:** `asso_qty` · **Cột vật lý:** `ASSO_QTY`

## Ý nghĩa nghiệp vụ

Số lượng thành phần trong combo trên dòng bán STRANS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `ASSO_QTY` | numeric | Số lượng trong combo |
| `db2:strans` | `ASSO_QTY` | numeric | Số lượng trong combo |
| `db2:strans_tmp` | `ASSO_QTY` | numeric | Số lượng trong combo |
| `db2:suspend` | `ASSO_QTY` | numeric | Số lượng trong combo |

## Ghi chú thêm

- Số lượng trong combo
