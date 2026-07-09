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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TRANS_CODE: top=221(773), 320(117), 113(54), 340(26), 310(22)'
- 'db2:strans.TRANS_CODE: top=221(871), 320(61), 113(48), 310(10), 318(5)'
- 'db2:strans_tmp.TRANS_CODE: top=221(999), 222(1)'
- 'db2:suspend.TRANS_CODE: top=221(1000)'
---

# Loại chứng từ dòng — 113=bán lẻ

**Semantic key:** `sale_line_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại chứng từ TRANS_CODE — bill bán lẻ (113). db1:strans: mã 113=bán lẻ (header/dòng); db2:strans: mã 113=bán lẻ (header/dòng); db2:strans_tmp: mã 211=?; db2:suspend: mã 221=thanh toán bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TRANS_CODE` | char | 113 = bán lẻ (line) |
| `db2:strans` | `TRANS_CODE` | char | 113 = bán lẻ (line) |
| `db2:strans_tmp` | `TRANS_CODE` | char | có dữ liệu |
| `db2:suspend` | `TRANS_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `113`×20

### `db2:strans.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `113`×20

### `db2:strans_tmp.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `211`×20

### `db2:suspend.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `221`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
