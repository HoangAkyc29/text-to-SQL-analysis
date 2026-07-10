---
semantic_key: type
title: type
display_names:
- TYPE
kind: text
tables:
- ref: db1:crdtrans_arc
  column: TYPE
  type: char
- ref: db2:barcode
  column: TYPE
  type: char
- ref: db2:crd_info
  column: TYPE
  type: char
- ref: db2:crdtrans
  column: TYPE
  type: char
- ref: db2:crdtrans_tmp
  column: TYPE
  type: char
- ref: db2:custhist
  column: TYPE
  type: char
- ref: db2:customer
  column: TYPE
  type: char
- ref: db2:partner
  column: TYPE
  type: char
- ref: db2:pmcrdinf
  column: TYPE
  type: char
- ref: db2:pmcrdiss
  column: TYPE
  type: char
- ref: db2:pmcrdrcv
  column: TYPE
  type: char
- ref: db2:pmcrdstk
  column: TYPE
  type: char
- ref: db2:supplier
  column: TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại bản ghi (ngữ cảnh theo bảng)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# type

**Semantic key:** `type` · **Cột vật lý:** `TYPE`

## Ý nghĩa nghiệp vụ

Loại bản ghi (ngữ cảnh theo bảng). Dùng trong Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …); Master / danh mục (BARCODE, CUSTOMER, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:barcode` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:crd_info` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:crdtrans` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:crdtrans_tmp` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:custhist` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:customer` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:partner` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:pmcrdinf` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:pmcrdiss` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:pmcrdrcv` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:pmcrdstk` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
| `db2:supplier` | `TYPE` | char | Loại bản ghi (ngữ cảnh theo bảng) |
