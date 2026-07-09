---
semantic_key: inv_no
title: inv no
display_names:
- INV_NO
kind: identifier
tables:
- ref: db1:strans
  column: INV_NO
  type: varchar
- ref: db2:ctrans
  column: INV_NO
  type: varchar
- ref: db2:debt
  column: INV_NO
  type: char
- ref: db2:inv_hdr
  column: INV_NO
  type: varchar
- ref: db2:inv_iss
  column: INV_NO
  type: varchar
- ref: db2:strans
  column: INV_NO
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Số hóa đơn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.INV_NO: top=1(10), 1710(1), 1217(1), 1275(1), 637(1)'
- 'db2:ctrans.INV_NO: top=1(252), 4(3), 66(2), 04(2), 1277(1)'
- 'db2:debt.INV_NO: top=1(64), 0000001(33), 456(2), 896(2), 1267(2)'
- 'db2:inv_hdr.INV_NO: top=1(21), 521(4), 632(4), 975(4), 1846(4)'
- 'db2:inv_iss.INV_NO: top=00000006(1)'
- 'db2:strans.INV_NO: top=1(15), 395(1), 172(1), 1946(1), 225(1)'
---

# inv no

**Semantic key:** `inv_no` · **Cột vật lý:** `INV_NO`

## Ý nghĩa nghiệp vụ

Cột INV_NO trên CTRANS, DEBT, INV_HDR. db1:strans: top 03, 1; db2:ctrans: top 1, 03, 04; db2:inv_hdr: top 1; db2:strans: top 04, 03, 1.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `INV_NO` | varchar | có dữ liệu |
| `db2:ctrans` | `INV_NO` | varchar | có dữ liệu |
| `db2:debt` | `INV_NO` | char | có dữ liệu |
| `db2:inv_hdr` | `INV_NO` | varchar | có dữ liệu |
| `db2:inv_iss` | `INV_NO` | varchar | có dữ liệu |
| `db2:strans` | `INV_NO` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.INV_NO`
- Null rate trong sample: 5%
- Distinct ≈2; top: `03`×10, `1`×9

### `db2:ctrans.INV_NO`
- Null rate trong sample: 35%
- Distinct ≈4; top: `1`×10, `03`×1, `04`×1, `18`×1

### `db2:inv_hdr.INV_NO`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:strans.INV_NO`
- Null rate trong sample: 5%
- Distinct ≈3; top: `04`×8, `03`×7, `1`×4

## Ghi chú thêm

- Số hóa đơn
