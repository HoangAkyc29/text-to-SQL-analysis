---
semantic_key: stk_dtl__frsupp_amt
title: stk dtl · frsupp amt
display_names:
- FRSUPP_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRSUPP_AMT
- 'db2:stk_dtl.FRSUPP_AMT: top=0.00(935), 72714000.00(1), 32848080.00(1), 64310000.00(1),
  50552832.00(1)'
---

# stk dtl · frsupp amt

**Semantic key:** `stk_dtl__frsupp_amt` · **Cột vật lý:** `FRSUPP_AMT`

## Ý nghĩa nghiệp vụ

Cột FRSUPP_AMT trên STK_DTL. db2:stk_dtl: top 0.00, 19161600.00, 456316000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRSUPP_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRSUPP_AMT`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0.00`×18, `19161600.00`×1, `456316000.00`×1

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_AMT
