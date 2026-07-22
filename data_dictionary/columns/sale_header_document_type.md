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
- Loại chứng từ trên header/line — nhiều mã đồng thời trên TRANSHDR/STRANS;
  map mã → ý nghĩa xem domain_definitions.md. Không mặc định một mã cho mọi query.
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Loại chứng từ (TRANS_CODE)

**Semantic key:** `sale_header_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại chứng từ trên header bill (`TRANSHDR`) và cũng xuất hiện trên dòng (`STRANS`). Nhiều mã cùng tồn tại; chỉ lọc khi brief yêu cầu một loại chứng từ cụ thể.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `TRANS_CODE` | char | Loại chứng từ archive — map mã trong domain_definitions.md |
| `db2:transhdr` | `TRANS_CODE` | char | Loại chứng từ live — map mã trong domain_definitions.md |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Map mã (`113`, `221`, `811`, …) → ý nghĩa: `domain_definitions.md`. Không suy ra mọi dòng bán/SKU đều cùng một `TRANS_CODE`.
