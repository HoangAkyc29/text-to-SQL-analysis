---
semantic_key: rdiscinf__gift
title: rdiscinf · gift
display_names:
- GIFT
kind: flag
tables:
- ref: db2:rdiscinf
  column: GIFT
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột GIFT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for GIFT
- 'db2:rdiscinf.GIFT: top=False(996), True(4)'
---

# rdiscinf · gift

**Semantic key:** `rdiscinf__gift` · **Cột vật lý:** `GIFT`

## Ý nghĩa nghiệp vụ

Cột GIFT trên RDISCINF. db2:rdiscinf: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `GIFT` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.GIFT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

