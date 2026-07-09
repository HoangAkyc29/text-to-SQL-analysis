---
semantic_key: time
title: time
display_names:
- TIME
kind: text
tables:
- ref: db2:hisrtpr
  column: TIME
  type: char
- ref: db2:hissppr
  column: TIME
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột TIME
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:hisrtpr.TIME: top=11:43(8), 16:36(7), 14:58(7), 11:23(6), 11:06(6)'
- 'db2:hissppr.TIME: top=10:55(8), 11:38(7), 16:52(7), 11:46(7), 11:13(7)'
---

# time

**Semantic key:** `time` · **Cột vật lý:** `TIME`

## Ý nghĩa nghiệp vụ

Cột TIME trên HISRTPR, HISSPPR. db2:hisrtpr: top 18:13, 10:16, 11:16; db2:hissppr: top 14:44, 14:42, 11:15.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hisrtpr` | `TIME` | char | có dữ liệu |
| `db2:hissppr` | `TIME` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hisrtpr.TIME`
- Null rate trong sample: 0%
- Distinct ≈16; top: `18:13`×3, `10:16`×2, `11:16`×2, `08:45`×1, `08:52`×1, `15:08`×1, `15:51`×1, `15:54`×1

### `db2:hissppr.TIME`
- Null rate trong sample: 0%
- Distinct ≈17; top: `14:44`×3, `14:42`×2, `11:15`×1, `11:21`×1, `14:40`×1, `14:43`×1, `14:56`×1, `14:59`×1

## Ghi chú thêm

