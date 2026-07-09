---
semantic_key: suspend__dtdisc_rate
title: suspend · dtdisc rate
display_names:
- DTDISC_RATE
kind: measure
tables:
- ref: db2:suspend
  column: DTDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệDTDISC_RATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DTDISC_RATE
- 'db2:suspend.DTDISC_RATE: top=0.00(1000)'
---

# suspend · dtdisc rate

**Semantic key:** `suspend__dtdisc_rate` · **Cột vật lý:** `DTDISC_RATE`

## Ý nghĩa nghiệp vụ

Cột DTDISC_RATE trên SUSPEND. db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:suspend` | `DTDISC_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:suspend.DTDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tỷ lệDTDISC_RATE
