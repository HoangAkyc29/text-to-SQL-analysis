---
semantic_key: rfn_amt
title: Số tiền hoàn trả (RFN_AMT)
display_names:
- RFN_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RFN_AMT
  type: numeric
- ref: db2:crd_info
  column: RFN_AMT
  type: numeric
- ref: db2:crdtrans
  column: RFN_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: RFN_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoàn / refund điểm: RFN_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền hoàn trả (RFN_AMT)

**Semantic key:** `rfn_amt` · **Cột vật lý:** `RFN_AMT`

## Ý nghĩa nghiệp vụ

Hoàn / refund điểm: RFN_AMT. Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `RFN_AMT` | numeric | Hoàn / refund điểm: RFN_AMT |
| `db2:crd_info` | `RFN_AMT` | numeric | Hoàn / refund điểm: RFN_AMT |
| `db2:crdtrans` | `RFN_AMT` | numeric | Hoàn / refund điểm: RFN_AMT |
| `db2:crdtrans_tmp` | `RFN_AMT` | numeric | Hoàn / refund điểm: RFN_AMT |
