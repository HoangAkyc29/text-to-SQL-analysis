---
semantic_key: suspend__dmdisc_amt
title: suspend · dmdisc amt
display_names:
- DMDISC_AMT
kind: measure
tables:
- ref: db2:suspend
  column: DMDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnDMDISC_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DMDISC_AMT
- 'db2:suspend.DMDISC_AMT: top=0.00(1000)'
---

# suspend · dmdisc amt

**Semantic key:** `suspend__dmdisc_amt` · **Cột vật lý:** `DMDISC_AMT`

## Ý nghĩa nghiệp vụ

Cột DMDISC_AMT trên SUSPEND. db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:suspend` | `DMDISC_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:suspend.DMDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiềnDMDISC_AMT
