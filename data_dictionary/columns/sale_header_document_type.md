---
semantic_key: sale_header_document_type
title: sale header document type
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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.TRANS_CODE: top=221(939), 113(45), 318(9), 310(4), 316(2)'
- 'db2:transhdr.TRANS_CODE: top=221(950), 113(35), 318(7), 310(4), 222(2)'
---

# sale header document type

**Semantic key:** `sale_header_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

TRANS_CODE trên TRANSHDR — 113 = header bill bán lẻ. Join STRANS/PMTRANS qua TRANS_NUM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `TRANS_CODE` | char | có dữ liệu |
| `db2:transhdr` | `TRANS_CODE` | char | 113 = header bill bán lẻ |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `221`×20

### `db2:transhdr.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `113`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
