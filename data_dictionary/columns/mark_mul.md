---
semantic_key: mark_mul
title: Hệ số nhân điểm tích lũy (MARK_MUL)
display_names:
- MARK_MUL
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: MARK_MUL
  type: numeric
- ref: db2:crdtrans
  column: MARK_MUL
  type: numeric
- ref: db2:crdtrans_tmp
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdinf
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdiss
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdrcv
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdstk
  column: MARK_MUL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Hệ số nhân điểm
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Hệ số nhân điểm tích lũy (MARK_MUL)

**Semantic key:** `mark_mul` · **Cột vật lý:** `MARK_MUL`

## Ý nghĩa nghiệp vụ

Hệ số nhân điểm. Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `MARK_MUL` | numeric | Hệ số nhân điểm |
| `db2:crdtrans` | `MARK_MUL` | numeric | Hệ số nhân điểm |
| `db2:crdtrans_tmp` | `MARK_MUL` | numeric | Hệ số nhân điểm |
| `db2:pmcrdinf` | `MARK_MUL` | numeric | Hệ số nhân điểm |
| `db2:pmcrdiss` | `MARK_MUL` | numeric | Hệ số nhân điểm |
| `db2:pmcrdrcv` | `MARK_MUL` | numeric | Hệ số nhân điểm |
| `db2:pmcrdstk` | `MARK_MUL` | numeric | Hệ số nhân điểm |
