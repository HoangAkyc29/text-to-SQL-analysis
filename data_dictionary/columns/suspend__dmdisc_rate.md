---
semantic_key: suspend__dmdisc_rate
title: suspend · dmdisc rate
display_names:
- DMDISC_RATE
kind: measure
tables:
- ref: db2:suspend
  column: DMDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệDMDISC_RATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DMDISC_RATE
- 'db2:suspend.DMDISC_RATE: top=0.00(1000)'
---

# suspend · dmdisc rate

**Semantic key:** `suspend__dmdisc_rate` · **Cột vật lý:** `DMDISC_RATE`

## Ý nghĩa nghiệp vụ

Cột DMDISC_RATE trên SUSPEND. db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:suspend` | `DMDISC_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:suspend.DMDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tỷ lệDMDISC_RATE
