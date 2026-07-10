---
semantic_key: stk_qty
title: Số lượng tồn kho (STK_QTY)
display_names:
- STK_QTY
kind: measure
tables:
- ref: db1:strans
  column: STK_QTY
  type: numeric
- ref: db2:hisrtpr
  column: STK_QTY
  type: numeric
- ref: db2:pmcrdstk
  column: STK_QTY
  type: numeric
- ref: db2:st_order
  column: STK_QTY
  type: numeric
- ref: db2:strans
  column: STK_QTY
  type: numeric
- ref: db2:strans_tmp
  column: STK_QTY
  type: numeric
- ref: db2:suspend
  column: STK_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng tồn / xuất kho
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng tồn kho (STK_QTY)

**Semantic key:** `stk_qty` · **Cột vật lý:** `STK_QTY`

## Ý nghĩa nghiệp vụ

Số lượng tồn kho hiện tại — snapshot hoặc movement tùy bảng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |
| `db2:hisrtpr` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |
| `db2:pmcrdstk` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |
| `db2:st_order` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |
| `db2:strans` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |
| `db2:strans_tmp` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |
| `db2:suspend` | `STK_QTY` | numeric | Số lượng tồn / xuất kho |

## Ghi chú thêm

- Số lượng tồn / xuất kho
