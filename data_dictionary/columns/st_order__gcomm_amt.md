---
semantic_key: st_order__gcomm_amt
title: st order · gcomm amt
display_names:
- GCOMM_AMT
kind: measure
tables:
- ref: db2:st_order
  column: GCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng gift: GCOMM_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for GCOMM_AMT
- 'db2:st_order.GCOMM_AMT: top=0.00(1000)'
---

# st order · gcomm amt

**Semantic key:** `st_order__gcomm_amt` · **Cột vật lý:** `GCOMM_AMT`

## Ý nghĩa nghiệp vụ

Cột GCOMM_AMT trên ST_ORDER. db2:st_order: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `GCOMM_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.GCOMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoa hồng gift: GCOMM_AMT
