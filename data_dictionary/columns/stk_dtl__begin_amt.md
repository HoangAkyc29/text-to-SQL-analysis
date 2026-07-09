---
semantic_key: stk_dtl__begin_amt
title: stk dtl · begin amt
display_names:
- BEGIN_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: BEGIN_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tồn đầu kỳ — giá trị
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEGIN_AMT
- 'db2:stk_dtl.BEGIN_AMT: top=0.00(808), 625000.00(2), 46000.00(1), 33348.00(1), -22610.00(1)'
---

# stk dtl · begin amt

**Semantic key:** `stk_dtl__begin_amt` · **Cột vật lý:** `BEGIN_AMT`

## Ý nghĩa nghiệp vụ

Cột BEGIN_AMT trên STK_DTL. db2:stk_dtl: top 0.00, -688620.00, 26.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `BEGIN_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.BEGIN_AMT`
- Null rate trong sample: 0%
- Distinct ≈15; top: `0.00`×6, `-688620.00`×1, `26.00`×1, `-20.00`×1, `-10.00`×1, `553200.00`×1, `194000.00`×1, `81000.00`×1

## Ghi chú thêm

- Tồn đầu kỳ — giá trị
