---
semantic_key: inv_date
title: inv date
display_names:
- INV_Date
- INV_DATE
kind: date
tables:
- ref: db1:strans
  column: INV_Date
  type: datetime
- ref: db2:ctrans
  column: INV_DATE
  type: datetime
- ref: db2:debt
  column: INV_Date
  type: datetime
- ref: db2:inv_hdr
  column: INV_DATE
  type: datetime
- ref: db2:inv_iss
  column: INV_DATE
  type: datetime
- ref: db2:strans
  column: INV_Date
  type: datetime
- ref: db2:strans_tmp
  column: INV_Date
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày hóa đơn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.INV_Date: top=2025-04-30 00:00:00(8), 2025-04-29 00:00:00(5), 2025-04-17
  00:00:00(3), 2025-04-11 00:00:00(2), 2025-04-26 00:00:00(2)'
- 'db2:ctrans.INV_DATE: top=2026-06-30 00:00:00(105), 2026-06-26 00:00:00(33), 2026-06-25
  00:00:00(30), 2026-06-24 00:00:00(26), 2026-06-15 00:00:00(25)'
- 'db2:debt.INV_Date: top=2025-07-31 00:00:00(3), 2022-01-20 00:00:00(3), 2025-12-31
  00:00:00(3), 2020-07-31 00:00:00(3), 2026-01-31 00:00:00(2)'
- 'db2:inv_hdr.INV_DATE: top=2024-09-18 00:00:00(5), 2024-01-09 00:00:00(4), 2025-11-28
  00:00:00(4), 2023-10-10 00:00:00(4), 2025-11-27 00:00:00(4)'
- 'db2:inv_iss.INV_DATE: top=2022-06-22 00:00:00(163), 2022-06-30 00:00:00(78), 2022-06-29
  00:00:00(51), 2022-06-17 00:00:00(17), 2022-06-24 00:00:00(14)'
- 'db2:strans.INV_Date: top=2026-06-30 00:00:00(9), 2026-06-17 00:00:00(4), 2026-06-05
  00:00:00(3), 2026-06-26 00:00:00(3), 2026-07-05 00:00:00(2)'
- 'db2:strans_tmp.INV_Date: top=2024-05-07 00:00:00(2), 2024-05-20 00:00:00(2), 2024-05-14
  00:00:00(2), 2024-05-06 00:00:00(2), 2024-05-15 00:00:00(1)'
---

# inv date

**Semantic key:** `inv_date` · **Cột vật lý:** `INV_Date`, `INV_DATE`

## Ý nghĩa nghiệp vụ

Cột INV_DATE trên CTRANS, DEBT, INV_HDR. db1:strans: top 2026-04-01T00:00:00, 2026-04-10T00:00:00; db2:ctrans: top 2026-06-03T00:00:00, 2026-06-01T00:00:00, 2026-06-02T00:00:00; db2:inv_hdr: top 2025-12-31T00:00:00, 2026-03-31T00:00:00, 2025-08-29T00:00:00; db2:inv_iss: top 2022-06-16T00:00:00; db2:strans: top 2026-06-01T00:00:00; db2:strans_tmp: top 2024-05-08T00:00:00, 2024-05-04T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `INV_Date` | datetime | có dữ liệu |
| `db2:ctrans` | `INV_DATE` | datetime | có dữ liệu |
| `db2:debt` | `INV_Date` | datetime | có dữ liệu |
| `db2:inv_hdr` | `INV_DATE` | datetime | có dữ liệu |
| `db2:inv_iss` | `INV_DATE` | datetime | có dữ liệu |
| `db2:strans` | `INV_Date` | datetime | có dữ liệu |
| `db2:strans_tmp` | `INV_Date` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.INV_Date`
- Null rate trong sample: 5%
- Distinct ≈2; top: `2026-04-01T00:00:00`×14, `2026-04-10T00:00:00`×5

### `db2:ctrans.INV_DATE`
- Null rate trong sample: 35%
- Distinct ≈3; top: `2026-06-03T00:00:00`×7, `2026-06-01T00:00:00`×3, `2026-06-02T00:00:00`×3

### `db2:inv_hdr.INV_DATE`
- Null rate trong sample: 0%
- Distinct ≈17; top: `2025-12-31T00:00:00`×3, `2026-03-31T00:00:00`×2, `2025-08-29T00:00:00`×1, `2025-08-31T00:00:00`×1, `2025-12-26T00:00:00`×1, `2026-01-22T00:00:00`×1, `2026-01-31T00:00:00`×1, `2026-02-09T00:00:00`×1

### `db2:inv_iss.INV_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2022-06-16T00:00:00`×20

### `db2:strans.INV_Date`
- Null rate trong sample: 5%
- Distinct ≈1; top: `2026-06-01T00:00:00`×19

### `db2:strans_tmp.INV_Date`
- Null rate trong sample: 35%
- Distinct ≈2; top: `2024-05-08T00:00:00`×11, `2024-05-04T00:00:00`×2

## Ghi chú thêm

- Ngày hóa đơn
