---
semantic_key: rfn_rate
title: Tỷ lệ hoàn trả (%) (RFN_RATE)
display_names:
- RFN_RATE
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RFN_RATE
  type: numeric
- ref: db2:crdtrans
  column: RFN_RATE
  type: numeric
- ref: db2:crdtrans_tmp
  column: RFN_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoàn / refund điểm: RFN_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ hoàn trả (%) (RFN_RATE)

**Semantic key:** `rfn_rate` · **Cột vật lý:** `RFN_RATE`

## Ý nghĩa nghiệp vụ

Hoàn / refund điểm: RFN_RATE. Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `RFN_RATE` | numeric | Hoàn / refund điểm: RFN_RATE |
| `db2:crdtrans` | `RFN_RATE` | numeric | Hoàn / refund điểm: RFN_RATE |
| `db2:crdtrans_tmp` | `RFN_RATE` | numeric | Hoàn / refund điểm: RFN_RATE |
