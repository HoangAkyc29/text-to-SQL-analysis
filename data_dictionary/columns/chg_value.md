---
semantic_key: chg_value
title: chg value
display_names:
- CHG_VALUE
kind: measure
tables:
- ref: db2:pmcrdiss
  column: CHG_VALUE
  type: numeric
- ref: db2:rdiscinf
  column: CHG_VALUE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột CHG_VALUE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdiss.CHG_VALUE: top=0.000(1000)'
- 'db2:rdiscinf.CHG_VALUE: top=4000.000(51), 3000.000(41), 2000.000(40), 10000.000(37),
  5000.000(35)'
---

# chg value

**Semantic key:** `chg_value` · **Cột vật lý:** `CHG_VALUE`

## Ý nghĩa nghiệp vụ

Cột CHG_VALUE trên PMCRDISS, RDISCINF. db2:pmcrdiss: top 0.000; db2:rdiscinf: top 20000.000, 15000.000, 30000.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdiss` | `CHG_VALUE` | numeric | có dữ liệu |
| `db2:rdiscinf` | `CHG_VALUE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdiss.CHG_VALUE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:rdiscinf.CHG_VALUE`
- Null rate trong sample: 0%
- Distinct ≈14; top: `20000.000`×3, `15000.000`×2, `30000.000`×2, `10000.000`×2, `50000.000`×2, `5000.000`×1, `16000.000`×1, `11000.000`×1

## Ghi chú thêm

