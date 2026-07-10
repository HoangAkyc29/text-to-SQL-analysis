---
semantic_key: mark_val
title: Giá trị quy đổi điểm (MARK_VAL)
display_names:
- MARK_VAL
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: MARK_VAL
  type: numeric
- ref: db2:crdtrans
  column: MARK_VAL
  type: numeric
- ref: db2:crdtrans_tmp
  column: MARK_VAL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá trị quy đổi điểm
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giá trị quy đổi điểm (MARK_VAL)

**Semantic key:** `mark_val` · **Cột vật lý:** `MARK_VAL`

## Ý nghĩa nghiệp vụ

Giá trị quy đổi điểm. Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `MARK_VAL` | numeric | Giá trị quy đổi điểm |
| `db2:crdtrans` | `MARK_VAL` | numeric | Giá trị quy đổi điểm |
| `db2:crdtrans_tmp` | `MARK_VAL` | numeric | Giá trị quy đổi điểm |
