---
semantic_key: pmcrdrcv__ref_amt
title: pmcrdrcv · ref amt
display_names:
- REF_AMT
kind: measure
tables:
- ref: db2:pmcrdrcv
  column: REF_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnREF_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for REF_AMT
- 'db2:pmcrdrcv.REF_AMT: top=0(1000)'
---

# pmcrdrcv · ref amt

**Semantic key:** `pmcrdrcv__ref_amt` · **Cột vật lý:** `REF_AMT`

## Ý nghĩa nghiệp vụ

Cột REF_AMT trên PMCRDRCV. db2:pmcrdrcv: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdrcv` | `REF_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdrcv.REF_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số tiềnREF_AMT
