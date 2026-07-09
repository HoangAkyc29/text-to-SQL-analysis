---
semantic_key: rdiscinf__chg_type
title: rdiscinf · chg type
display_names:
- CHG_TYPE
kind: text
tables:
- ref: db2:rdiscinf
  column: CHG_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột CHG_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CHG_TYPE
- 'db2:rdiscinf.CHG_TYPE: top=02(949), 01(29), 03(22)'
---

# rdiscinf · chg type

**Semantic key:** `rdiscinf__chg_type` · **Cột vật lý:** `CHG_TYPE`

## Ý nghĩa nghiệp vụ

Cột CHG_TYPE trên RDISCINF. db2:rdiscinf: top 02.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `CHG_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.CHG_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `02`×20

## Ghi chú thêm

