---
semantic_key: stk_dtl__tocust_amt
title: stk dtl · tocust amt
display_names:
- TOCUST_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCUST_AMT
- 'db2:stk_dtl.TOCUST_AMT: top=0.00(880), 95912080.00(1), 3028516.00(1), 58369500.00(1),
  7028100.00(1)'
---

# stk dtl · tocust amt

**Semantic key:** `stk_dtl__tocust_amt` · **Cột vật lý:** `TOCUST_AMT`

## Ý nghĩa nghiệp vụ

Cột TOCUST_AMT trên STK_DTL. db2:stk_dtl: top 0.00, 14251440.00, 497172294.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCUST_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCUST_AMT`
- Null rate trong sample: 0%
- Distinct ≈4; top: `0.00`×17, `14251440.00`×1, `497172294.00`×1, `6596000.00`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_AMT
