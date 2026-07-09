---
semantic_key: pmcrdinf__stk_date
title: pmcrdinf · stk date
display_names:
- STK_DATE
kind: date
tables:
- ref: db2:pmcrdinf
  column: STK_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàySTK_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STK_DATE
- 'db2:pmcrdinf.STK_DATE: top=2020-10-01 00:00:00(7), 2021-06-30 00:00:00(6), 2020-11-14
  00:00:00(6), 2025-12-08 00:00:00(6), 2017-04-25 00:00:00(6)'
---

# pmcrdinf · stk date

**Semantic key:** `pmcrdinf__stk_date` · **Cột vật lý:** `STK_DATE`

## Ý nghĩa nghiệp vụ

Cột STK_DATE trên PMCRDINF. db2:pmcrdinf: top 2012-12-26T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `STK_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.STK_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-12-26T00:00:00`×20

## Ghi chú thêm

- NgàySTK_DATE
