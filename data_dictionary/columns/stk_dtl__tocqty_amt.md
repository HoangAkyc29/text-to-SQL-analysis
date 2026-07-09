---
semantic_key: stk_dtl__tocqty_amt
title: stk dtl · tocqty amt
display_names:
- TOCQTY_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCQTY_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCQTY_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCQTY_AMT
- 'db2:stk_dtl.TOCQTY_AMT: top=0.00(1000)'
---

# stk dtl · tocqty amt

**Semantic key:** `stk_dtl__tocqty_amt` · **Cột vật lý:** `TOCQTY_AMT`

## Ý nghĩa nghiệp vụ

Cột TOCQTY_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCQTY_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCQTY_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCQTY_AMT
