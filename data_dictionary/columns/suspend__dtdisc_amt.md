---
semantic_key: suspend__dtdisc_amt
title: suspend · dtdisc amt
display_names:
- DTDISC_AMT
kind: measure
tables:
- ref: db2:suspend
  column: DTDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnDTDISC_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DTDISC_AMT
- 'db2:suspend.DTDISC_AMT: top=0.00(1000)'
---

# suspend · dtdisc amt

**Semantic key:** `suspend__dtdisc_amt` · **Cột vật lý:** `DTDISC_AMT`

## Ý nghĩa nghiệp vụ

Cột DTDISC_AMT trên SUSPEND. db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:suspend` | `DTDISC_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:suspend.DTDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiềnDTDISC_AMT
