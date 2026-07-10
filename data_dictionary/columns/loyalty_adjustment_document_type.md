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
- column_semantic_registry
- business_prose
---

# Loại GD điều chỉnh/đổi quà — 812 (CRDTRANS_ARC db1)

**Semantic key:** `loyalty_adjustment_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại giao dịch điều chỉnh / đổi quà (TRANS_CODE=812 trên CRDTRANS_ARC db1).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `TRANS_CODE` | char | 812 = điều chỉnh / đổi quà / trừ điểm |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
