---
semantic_key: pmcrdstk__rcv_qty
title: Số lượng (PMCRDSTK)
display_names:
- RCV_QTY
kind: measure
tables:
- ref: db2:pmcrdstk
  column: RCV_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- SL nhận
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (PMCRDSTK)

**Semantic key:** `pmcrdstk__rcv_qty` · **Cột vật lý:** `RCV_QTY`

## Ý nghĩa nghiệp vụ

Số lượng — bảng PMCRDSTK.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdstk` | `RCV_QTY` | numeric | SL nhận |

## Ghi chú thêm

- SL nhận
