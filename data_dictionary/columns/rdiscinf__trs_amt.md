---
semantic_key: rdiscinf__trs_amt
title: rdiscinf · trs amt
display_names:
- TRS_AMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: TRS_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnTRS_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TRS_AMT
- 'db2:rdiscinf.TRS_AMT: top=0.00(1000)'
---

# rdiscinf · trs amt

**Semantic key:** `rdiscinf__trs_amt` · **Cột vật lý:** `TRS_AMT`

## Ý nghĩa nghiệp vụ

Cột TRS_AMT trên RDISCINF. db2:rdiscinf: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `TRS_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.TRS_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiềnTRS_AMT
