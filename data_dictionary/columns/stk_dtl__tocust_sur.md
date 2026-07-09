---
semantic_key: stk_dtl__tocust_sur
title: stk dtl · tocust sur
display_names:
- TOCUST_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCUST_SUR
- 'db2:stk_dtl.TOCUST_SUR: top=0.00(877), 816000.00(2), 53850924.34(1), 478520.76(1),
  13526333.73(1)'
---

# stk dtl · tocust sur

**Semantic key:** `stk_dtl__tocust_sur` · **Cột vật lý:** `TOCUST_SUR`

## Ý nghĩa nghiệp vụ

Cột TOCUST_SUR trên STK_DTL. db2:stk_dtl: top 0.00, 3201894.24, 31293000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCUST_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCUST_SUR`
- Null rate trong sample: 0%
- Distinct ≈6; top: `0.00`×15, `3201894.24`×1, `31293000.00`×1, `51903702.76`×1, `127054942.58`×1, `2448000.00`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_SUR
