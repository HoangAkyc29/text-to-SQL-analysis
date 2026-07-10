---
semantic_key: payment_document_type
title: Loại chứng từ thanh toán — 221/222/008
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db1:pmtrans
  column: TRANS_CODE
  type: char
- ref: db2:pmtrans
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

# Loại chứng từ thanh toán — 221/222/008

**Semantic key:** `payment_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Phân loại loại chứng từ trong hệ POS/ERP. 113 = bán lẻ; 221 = thanh toán bill; 811/812 = tích điểm / điều chỉnh loyalty — grain phụ thuộc bảng. Chỉ xuất hiện trên dòng thanh toán / quỹ bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `TRANS_CODE` | char | 221 thanh toán bill, 222/008 chi quỹ hoặc điều chỉnh |
| `db2:pmtrans` | `TRANS_CODE` | char | 221 thanh toán bill, 222/008 chi quỹ hoặc điều chỉnh |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
