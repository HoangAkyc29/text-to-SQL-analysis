---
semantic_key: debt__fine_amt
title: Số tiền phạt chậm trả (DEBT)
display_names:
- FINE_AMT
kind: measure
tables:
- ref: db2:debt
  column: FINE_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnFINE_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền phạt chậm trả (DEBT)

**Semantic key:** `debt__fine_amt` · **Cột vật lý:** `FINE_AMT`

## Ý nghĩa nghiệp vụ

Tiền phạt chậm trả / phí phạt trên công nợ DEBT.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:debt` | `FINE_AMT` | numeric | Số tiềnFINE_AMT |

## Ghi chú thêm

- Số tiềnFINE_AMT
