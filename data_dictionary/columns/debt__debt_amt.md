---
semantic_key: debt__debt_amt
title: debt · debt amt
display_names:
- DEBT_AMT
kind: measure
tables:
- ref: db2:debt
  column: DEBT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền công nợ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DEBT_AMT
- 'db2:debt.DEBT_AMT: top=15840000.00(5), 10800000.00(4), 19800000.00(4), 4320000.00(3),
  11880000.00(3)'
---

# debt · debt amt

**Semantic key:** `debt__debt_amt` · **Cột vật lý:** `DEBT_AMT`

## Ý nghĩa nghiệp vụ

Cột DEBT_AMT trên DEBT. db2:debt: top 46995908.40, 51202166.40, 69743567.52.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:debt` | `DEBT_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:debt.DEBT_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `46995908.40`×1, `51202166.40`×1, `69743567.52`×1, `55835099.10`×1, `32262271.65`×1, `113998950.45`×1, `62726400.00`×1, `87501150.00`×1

## Ghi chú thêm

- Số tiền công nợ
