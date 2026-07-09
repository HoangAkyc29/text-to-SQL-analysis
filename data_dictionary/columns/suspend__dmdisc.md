---
semantic_key: suspend__dmdisc
title: suspend · dmdisc
display_names:
- DMDISC
kind: flag
tables:
- ref: db2:suspend
  column: DMDISC
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột DMDISC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DMDISC
- 'db2:suspend.DMDISC: top=False(1000)'
---

# suspend · dmdisc

**Semantic key:** `suspend__dmdisc` · **Cột vật lý:** `DMDISC`

## Ý nghĩa nghiệp vụ

Cột DMDISC trên SUSPEND. db2:suspend: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:suspend` | `DMDISC` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:suspend.DMDISC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

