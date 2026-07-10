---
semantic_key: iss_qty
title: Số lượng xuất kho (ISS_QTY)
display_names:
- ISS_QTY
kind: measure
tables:
- ref: db2:pmcrdiss
  column: ISS_QTY
  type: numeric
- ref: db2:pmcrdstk
  column: ISS_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- SL xuất
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng xuất kho (ISS_QTY)

**Semantic key:** `iss_qty` · **Cột vật lý:** `ISS_QTY`

## Ý nghĩa nghiệp vụ

SL xuất. Dùng trong bảng PMCRDISS, bảng PMCRDSTK.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdiss` | `ISS_QTY` | numeric | SL xuất |
| `db2:pmcrdstk` | `ISS_QTY` | numeric | SL xuất |
