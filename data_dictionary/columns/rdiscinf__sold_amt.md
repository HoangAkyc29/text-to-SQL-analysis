---
semantic_key: rdiscinf__sold_amt
title: rdiscinf · sold amt
display_names:
- SOLD_AMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: SOLD_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnSOLD_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SOLD_AMT
- 'db2:rdiscinf.SOLD_AMT: top=0(1000)'
---

# rdiscinf · sold amt

**Semantic key:** `rdiscinf__sold_amt` · **Cột vật lý:** `SOLD_AMT`

## Ý nghĩa nghiệp vụ

Cột SOLD_AMT trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `SOLD_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.SOLD_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số tiềnSOLD_AMT
