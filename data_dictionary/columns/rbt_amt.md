---
semantic_key: rbt_amt
title: Số tiền rebate (RBT_AMT)
display_names:
- RBT_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RBT_AMT
  type: numeric
- ref: db2:crdtrans
  column: RBT_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: RBT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Rebate: RBT_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền rebate (RBT_AMT)

**Semantic key:** `rbt_amt` · **Cột vật lý:** `RBT_AMT`

## Ý nghĩa nghiệp vụ

Rebate: RBT_AMT. Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `RBT_AMT` | numeric | Rebate: RBT_AMT |
| `db2:crdtrans` | `RBT_AMT` | numeric | Rebate: RBT_AMT |
| `db2:crdtrans_tmp` | `RBT_AMT` | numeric | Rebate: RBT_AMT |
