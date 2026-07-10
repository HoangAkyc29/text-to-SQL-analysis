---
semantic_key: sale_line_document_type
title: Loại chứng từ dòng — 113=bán lẻ
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db1:strans
  column: TRANS_CODE
  type: char
- ref: db2:strans
  column: TRANS_CODE
  type: char
- ref: db2:strans_tmp
  column: TRANS_CODE
  type: char
- ref: db2:suspend
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

# Loại chứng từ dòng — 113=bán lẻ

**Semantic key:** `sale_line_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Phân loại loại chứng từ trong hệ POS/ERP. 113 = bán lẻ; 221 = thanh toán bill; 811/812 = tích điểm / điều chỉnh loyalty — grain phụ thuộc bảng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TRANS_CODE` | char | 113 = dòng bán lẻ POS |
| `db2:strans` | `TRANS_CODE` | char | 113 = dòng bán lẻ POS |
| `db2:strans_tmp` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:suspend` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
