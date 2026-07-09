---
semantic_key: pmcrdinf__cond_amt
title: pmcrdinf · cond amt
display_names:
- COND_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: COND_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnCOND_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for COND_AMT
- 'db2:pmcrdinf.COND_AMT: top=0(1000)'
---

# pmcrdinf · cond amt

**Semantic key:** `pmcrdinf__cond_amt` · **Cột vật lý:** `COND_AMT`

## Ý nghĩa nghiệp vụ

Cột COND_AMT trên PMCRDINF. db2:pmcrdinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `COND_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.COND_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số tiềnCOND_AMT
