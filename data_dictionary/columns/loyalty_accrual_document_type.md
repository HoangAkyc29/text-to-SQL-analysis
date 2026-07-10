---
semantic_key: loyalty_accrual_document_type
title: Loại GD tích điểm live — 811 (CRDTRANS db2)
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db2:crdtrans
  column: TRANS_CODE
  type: char
- ref: db2:crdtrans_tmp
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

# Loại GD tích điểm live — 811 (CRDTRANS db2)

**Semantic key:** `loyalty_accrual_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại giao dịch tích điểm live (TRANS_CODE=811 trên CRDTRANS db2).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crdtrans` | `TRANS_CODE` | char | 811 = tích điểm từ mua hàng |
| `db2:crdtrans_tmp` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
