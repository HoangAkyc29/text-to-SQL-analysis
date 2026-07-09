---
semantic_key: debt_date
title: debt date
display_names:
- DEBT_DATE
kind: date
tables:
- ref: db2:ctrans
  column: DEBT_DATE
  type: datetime
- ref: db2:debt
  column: DEBT_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày phát sinh công nợ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:ctrans.DEBT_DATE: top=2026-06-30 00:00:00(276), 2026-06-26 00:00:00(60), 2026-06-25
  00:00:00(50), 2026-06-15 00:00:00(47), 2026-06-24 00:00:00(36)'
- 'db2:debt.DEBT_DATE: top=2025-12-31 00:00:00(7), 2025-07-31 00:00:00(5), 2024-03-31
  00:00:00(5), 2024-12-31 00:00:00(5), 2022-07-31 00:00:00(5)'
---

# debt date

**Semantic key:** `debt_date` · **Cột vật lý:** `DEBT_DATE`

## Ý nghĩa nghiệp vụ

Cột DEBT_DATE trên CTRANS, DEBT. db2:ctrans: top 2026-06-03T00:00:00, 2026-06-02T00:00:00, 2026-06-01T00:00:00; db2:debt: top 2012-12-01T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `DEBT_DATE` | datetime | có dữ liệu |
| `db2:debt` | `DEBT_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.DEBT_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-06-03T00:00:00`×11, `2026-06-02T00:00:00`×5, `2026-06-01T00:00:00`×4

### `db2:debt.DEBT_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-12-01T00:00:00`×20

## Ghi chú thêm

- Ngày phát sinh công nợ
