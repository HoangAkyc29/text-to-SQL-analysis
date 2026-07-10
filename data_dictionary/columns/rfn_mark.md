---
semantic_key: rfn_mark
title: Điểm hoàn / điểm trả lại (RFN_MARK)
display_names:
- RFN_MARK
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RFN_MARK
  type: numeric
- ref: db2:crdtrans
  column: RFN_MARK
  type: numeric
- ref: db2:crdtrans_tmp
  column: RFN_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoàn / refund điểm: RFN_MARK'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Điểm hoàn / điểm trả lại (RFN_MARK)

**Semantic key:** `rfn_mark` · **Cột vật lý:** `RFN_MARK`

## Ý nghĩa nghiệp vụ

Hoàn / refund điểm: RFN_MARK. Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `RFN_MARK` | numeric | Hoàn / refund điểm: RFN_MARK |
| `db2:crdtrans` | `RFN_MARK` | numeric | Hoàn / refund điểm: RFN_MARK |
| `db2:crdtrans_tmp` | `RFN_MARK` | numeric | Hoàn / refund điểm: RFN_MARK |
