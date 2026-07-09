---
semantic_key: pmcrdinf__bal_amt
title: pmcrdinf · bal amt
display_names:
- BAL_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: BAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số dư
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BAL_AMT
- 'db2:pmcrdinf.BAL_AMT: top=0.00(1000)'
---

# pmcrdinf · bal amt

**Semantic key:** `pmcrdinf__bal_amt` · **Cột vật lý:** `BAL_AMT`

## Ý nghĩa nghiệp vụ

Cột BAL_AMT trên PMCRDINF. db2:pmcrdinf: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `BAL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.BAL_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số dư
