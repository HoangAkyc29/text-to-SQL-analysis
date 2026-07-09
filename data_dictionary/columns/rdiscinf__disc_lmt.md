---
semantic_key: rdiscinf__disc_lmt
title: rdiscinf · disc lmt
display_names:
- DISC_LMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: DISC_LMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DISC_LMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISC_LMT
- 'db2:rdiscinf.DISC_LMT: top=0.00(1000)'
---

# rdiscinf · disc lmt

**Semantic key:** `rdiscinf__disc_lmt` · **Cột vật lý:** `DISC_LMT`

## Ý nghĩa nghiệp vụ

Cột DISC_LMT trên RDISCINF. db2:rdiscinf: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `DISC_LMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.DISC_LMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

