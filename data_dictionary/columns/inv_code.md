---
semantic_key: inv_code
title: inv code
display_names:
- INV_CODE
kind: code
tables:
- ref: db1:strans
  column: INV_CODE
  type: varchar
- ref: db2:ctrans
  column: INV_CODE
  type: varchar
- ref: db2:debt
  column: INV_CODE
  type: varchar
- ref: db2:inv_hdr
  column: INV_CODE
  type: varchar
- ref: db2:inv_iss
  column: INV_CODE
  type: varchar
- ref: db2:strans
  column: INV_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã serial HĐ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.INV_CODE: top=1(31)'
- 'db2:ctrans.INV_CODE: top=1(584), 4(3)'
- 'db2:debt.INV_CODE: top=1(332), 0(2)'
- 'db2:inv_hdr.INV_CODE: top=1(997), 0(1), 4(1), 1748(1)'
- 'db2:inv_iss.INV_CODE: top=1(120)'
- 'db2:strans.INV_CODE: top=1(39)'
---

# inv code

**Semantic key:** `inv_code` · **Cột vật lý:** `INV_CODE`

## Ý nghĩa nghiệp vụ

Cột INV_CODE trên CTRANS, DEBT, INV_HDR. db1:strans: top 1; db2:ctrans: top 1; db2:inv_hdr: top 1; db2:strans: top 1.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `INV_CODE` | varchar | có dữ liệu |
| `db2:ctrans` | `INV_CODE` | varchar | có dữ liệu |
| `db2:debt` | `INV_CODE` | varchar | có dữ liệu |
| `db2:inv_hdr` | `INV_CODE` | varchar | có dữ liệu |
| `db2:inv_iss` | `INV_CODE` | varchar | có dữ liệu |
| `db2:strans` | `INV_CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.INV_CODE`
- Null rate trong sample: 5%
- Distinct ≈1; top: `1`×19

### `db2:ctrans.INV_CODE`
- Null rate trong sample: 35%
- Distinct ≈1; top: `1`×13

### `db2:inv_hdr.INV_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:strans.INV_CODE`
- Null rate trong sample: 5%
- Distinct ≈1; top: `1`×19

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã serial HĐ
