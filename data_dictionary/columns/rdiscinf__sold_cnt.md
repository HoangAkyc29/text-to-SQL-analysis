---
semantic_key: rdiscinf__sold_cnt
title: rdiscinf · sold cnt
display_names:
- SOLD_CNT
kind: measure
tables:
- ref: db2:rdiscinf
  column: SOLD_CNT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột SOLD_CNT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SOLD_CNT
- 'db2:rdiscinf.SOLD_CNT: top=0(1000)'
---

# rdiscinf · sold cnt

**Semantic key:** `rdiscinf__sold_cnt` · **Cột vật lý:** `SOLD_CNT`

## Ý nghĩa nghiệp vụ

Cột SOLD_CNT trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `SOLD_CNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.SOLD_CNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

