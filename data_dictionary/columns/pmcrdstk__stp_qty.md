---
semantic_key: pmcrdstk__stp_qty
title: Số lượng (PMCRDSTK)
display_names:
- STP_QTY
kind: measure
tables:
- ref: db2:pmcrdstk
  column: STP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- SL dừng/hủy
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (PMCRDSTK)

**Semantic key:** `pmcrdstk__stp_qty` · **Cột vật lý:** `STP_QTY`

## Ý nghĩa nghiệp vụ

Số lượng — bảng PMCRDSTK.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdstk` | `STP_QTY` | numeric | SL dừng/hủy |

## Ghi chú thêm

- SL dừng/hủy
