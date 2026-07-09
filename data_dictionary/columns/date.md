---
semantic_key: date
title: date
display_names:
- DATE
kind: date
tables:
- ref: db2:hisrtpr
  column: DATE
  type: datetime
- ref: db2:hissppr
  column: DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Cột DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:hisrtpr.DATE: top=2025-09-11 11:43:31(3), 2026-06-15 09:29:59(3), 2025-09-17
  11:06:52(2), 2025-12-28 16:31:08(2), 2025-04-24 17:48:07(2)'
- 'db2:hissppr.DATE: top=2025-09-13 10:06:10(1), 2022-05-05 13:53:15(1), 2022-08-05
  11:38:28(1), 2023-11-17 16:10:10(1), 2022-10-31 15:47:34(1)'
---

# date

**Semantic key:** `date` · **Cột vật lý:** `DATE`

## Ý nghĩa nghiệp vụ

Cột DATE trên HISRTPR, HISSPPR. db2:hisrtpr: top 2022-03-09T08:45:14, 2022-03-09T08:52:30, 2022-03-09T10:16:10; db2:hissppr: top 2022-03-16T11:15:12, 2022-03-16T11:21:21, 2022-03-16T14:40:50.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hisrtpr` | `DATE` | datetime | có dữ liệu |
| `db2:hissppr` | `DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hisrtpr.DATE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `2022-03-09T08:45:14`×1, `2022-03-09T08:52:30`×1, `2022-03-09T10:16:10`×1, `2022-03-09T10:16:32`×1, `2022-03-09T15:08:27`×1, `2022-03-09T15:51:11`×1, `2022-03-09T15:54:03`×1, `2022-03-09T16:56:22`×1

### `db2:hissppr.DATE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `2022-03-16T11:15:12`×1, `2022-03-16T11:21:21`×1, `2022-03-16T14:40:50`×1, `2022-03-16T14:42:05`×1, `2022-03-16T14:42:46`×1, `2022-03-16T14:43:13`×1, `2022-03-16T14:44:06`×1, `2022-03-16T14:44:41`×1

## Ghi chú thêm

