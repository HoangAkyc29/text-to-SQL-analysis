---
semantic_key: trans_code
title: trans code
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db2:cash_st
  column: TRANS_CODE
  type: char
- ref: db2:ctrans
  column: TRANS_CODE
  type: char
- ref: db2:custhist
  column: TRANS_CODE
  type: char
- ref: db2:inv_iss
  column: TRANS_CODE
  type: char
- ref: db2:pmcrdiss
  column: TRANS_CODE
  type: char
- ref: db2:pmcrdrcv
  column: TRANS_CODE
  type: char
- ref: db2:pmcrdstk
  column: TRANS_CODE
  type: char
- ref: db2:st_order
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
- 'db2:cash_st.TRANS_CODE: top=010(1000)'
- 'db2:ctrans.TRANS_CODE: top=113(958), 211(33), 115(9)'
- 'db2:custhist.TRANS_CODE: top=113(853), 211(116), 133(31)'
- 'db2:inv_iss.TRANS_CODE: top=221(360)'
- 'db2:pmcrdiss.TRANS_CODE: top=821(702), 824(298)'
- 'db2:pmcrdrcv.TRANS_CODE: top=221(1000)'
- 'db2:pmcrdstk.TRANS_CODE: top=821(1000)'
- 'db2:st_order.TRANS_CODE: top=334(1000)'
---

# trans code

**Semantic key:** `trans_code` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại chứng từ TRANS_CODE theo bảng. db2:cash_st: mã 010=?; db2:ctrans: mã 113=bán lẻ (header/dòng); db2:custhist: mã 113=bán lẻ (header/dòng); db2:pmcrdiss: mã 821=xuất/nhập thẻ PM gift; db2:pmcrdrcv: mã 221=thanh toán bill; db2:pmcrdstk: mã 821=xuất/nhập thẻ PM gift; db2:st_order: mã 334=?.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cash_st` | `TRANS_CODE` | char | có dữ liệu |
| `db2:ctrans` | `TRANS_CODE` | char | có dữ liệu |
| `db2:custhist` | `TRANS_CODE` | char | có dữ liệu |
| `db2:inv_iss` | `TRANS_CODE` | char | có dữ liệu |
| `db2:pmcrdiss` | `TRANS_CODE` | char | có dữ liệu |
| `db2:pmcrdrcv` | `TRANS_CODE` | char | có dữ liệu |
| `db2:pmcrdstk` | `TRANS_CODE` | char | có dữ liệu |
| `db2:st_order` | `TRANS_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cash_st.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `010`×20

### `db2:ctrans.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `113`×20

### `db2:custhist.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `113`×20

### `db2:pmcrdiss.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `821`×20

### `db2:pmcrdrcv.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `221`×20

### `db2:pmcrdstk.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `821`×20

### `db2:st_order.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `334`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
