---
semantic_key: sale_header_document_type
title: Loại chứng từ (TRANS_CODE)
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db1:transhdr_arc
  column: TRANS_CODE
  type: char
- ref: db2:transhdr
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

# Loại chứng từ (TRANS_CODE)

**Semantic key:** `sale_header_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại chứng từ header bill (TRANSHDR) — 113 = bán lẻ POS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:transhdr` | `TRANS_CODE` | char | 113 = header bill bán lẻ |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
