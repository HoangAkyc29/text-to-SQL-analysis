---
semantic_key: sale_line_document_type
title: Loại chứng từ dòng STRANS — nhiều mã (221/113/…)
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

# Loại chứng từ dòng STRANS — nhiều mã (221/113/…)

**Semantic key:** `sale_line_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Phân loại chứng từ trên dòng `STRANS`. Có nhiều mã (`113`, `221`, `310`, …) — ý nghĩa và khi nào lọc lấy từ domain glossary + case study retrieve, không mặc định một mã cho mọi bài.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TRANS_CODE` | char | Nhiều mã chứng từ trên dòng hàng |
| `db2:strans` | `TRANS_CODE` | char | Nhiều mã; live thường nhiều `221` hơn `113` |
| `db2:strans_tmp` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md |
| `db2:suspend` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
