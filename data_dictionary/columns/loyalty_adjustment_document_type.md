---
semantic_key: loyalty_adjustment_document_type
title: Loại GD điều chỉnh/đổi quà — 812 (CRDTRANS_ARC db1)
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db1:crdtrans_arc
  column: TRANS_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ,
  008=quỹ, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.TRANS_CODE: top=221(989), 812(7), 811(3), 222(1)'
---

# Loại GD điều chỉnh/đổi quà — 812 (CRDTRANS_ARC db1)

**Semantic key:** `loyalty_adjustment_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

TRANS_CODE=812 trên CRDTRANS_ARC (db1 archive) — điều chỉnh thủ công, đổi quà, trừ điểm.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `TRANS_CODE` | char | 812 = điều chỉnh/đổi quà |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `812`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
