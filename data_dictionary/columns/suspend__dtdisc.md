---
semantic_key: suspend__dtdisc
title: suspend · dtdisc
display_names:
- DTDISC
kind: flag
tables:
- ref: db2:suspend
  column: DTDISC
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột DTDISC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DTDISC
- 'db2:suspend.DTDISC: top=False(1000)'
---

# suspend · dtdisc

**Semantic key:** `suspend__dtdisc` · **Cột vật lý:** `DTDISC`

## Ý nghĩa nghiệp vụ

Cột DTDISC trên SUSPEND. db2:suspend: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:suspend` | `DTDISC` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:suspend.DTDISC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

