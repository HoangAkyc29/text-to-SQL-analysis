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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.TYPE: top=01(1000)'
- 'db2:barcode.TYPE: top=01(998), 03(2)'
- 'db2:crd_info.TYPE: top=01(1000)'
- 'db2:crdtrans.TYPE: top=01(1000)'
- 'db2:crdtrans_tmp.TYPE: top=01(1000)'
- 'db2:custhist.TYPE: top=05(857), 04(116), 06(27)'
- 'db2:customer.TYPE: top=03(998)'
- 'db2:partner.TYPE: top=05(919), 06(65), 04(14), 03(2)'
- 'db2:pmcrdinf.TYPE: top=11(999), 03(1)'
- 'db2:pmcrdiss.TYPE: top=11(596), 06(1)'
- 'db2:pmcrdrcv.TYPE: top=11(1000)'
- 'db2:pmcrdstk.TYPE: top=11(1000)'
- 'db2:supplier.TYPE: top=05(935), 06(65)'
---

# type

**Semantic key:** `type` · **Cột vật lý:** `TYPE`

## Ý nghĩa nghiệp vụ

Cột TYPE trên BARCODE, CRDTRANS, CRDTRANS_ARC. db1:crdtrans_arc: top 01; db2:barcode: top 01; db2:crd_info: top 01; db2:crdtrans: top 01; db2:crdtrans_tmp: top 01; db2:custhist: top 05; db2:customer: top 03; db2:partner: top 05; db2:pmcrdinf: top 11; db2:pmcrdrcv: top 11; db2:pmcrdstk: top 11; db2:supplier: top 05.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `TYPE` | char | có dữ liệu |
| `db2:barcode` | `TYPE` | char | có dữ liệu |
| `db2:crd_info` | `TYPE` | char | có dữ liệu |
| `db2:crdtrans` | `TYPE` | char | có dữ liệu |
| `db2:crdtrans_tmp` | `TYPE` | char | có dữ liệu |
| `db2:custhist` | `TYPE` | char | có dữ liệu |
| `db2:customer` | `TYPE` | char | có dữ liệu |
| `db2:partner` | `TYPE` | char | có dữ liệu |
| `db2:pmcrdinf` | `TYPE` | char | có dữ liệu |
| `db2:pmcrdiss` | `TYPE` | char | có dữ liệu |
| `db2:pmcrdrcv` | `TYPE` | char | có dữ liệu |
| `db2:pmcrdstk` | `TYPE` | char | có dữ liệu |
| `db2:supplier` | `TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:barcode.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:crd_info.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:crdtrans.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:crdtrans_tmp.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:custhist.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

### `db2:customer.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `03`×20

### `db2:partner.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

### `db2:pmcrdinf.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `11`×20

### `db2:pmcrdrcv.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `11`×20

### `db2:pmcrdstk.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `11`×20

### `db2:supplier.TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

## Ghi chú thêm

- Loại bản ghi (ngữ cảnh theo bảng)
