---
semantic_key: buy_mark
title: buy mark
display_names:
- BUY_MARK
kind: measure
tables:
- ref: db2:pmcrdinf
  column: BUY_MARK
  type: numeric
- ref: db2:pmcrdiss
  column: BUY_MARK
  type: numeric
- ref: db2:pmcrdrcv
  column: BUY_MARK
  type: numeric
- ref: db2:pmcrdstk
  column: BUY_MARK
  type: numeric
- ref: db2:rdiscinf
  column: BUY_MARK
  type: numeric
- ref: db2:sku_def
  column: BUY_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_MARK'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdinf.BUY_MARK: top=0(1000)'
- 'db2:pmcrdiss.BUY_MARK: top=0(1000)'
- 'db2:pmcrdrcv.BUY_MARK: top=0(1000)'
- 'db2:pmcrdstk.BUY_MARK: top=0(1000)'
- 'db2:rdiscinf.BUY_MARK: top=0(1000)'
- 'db2:sku_def.BUY_MARK: top=0.00(1000)'
---

# buy mark

**Semantic key:** `buy_mark` · **Cột vật lý:** `BUY_MARK`

## Ý nghĩa nghiệp vụ

Cột BUY_MARK trên PMCRDINF, PMCRDISS, PMCRDRCV. db2:pmcrdinf: top 0; db2:pmcrdiss: top 0; db2:pmcrdrcv: top 0; db2:pmcrdstk: top 0; db2:rdiscinf: top 0; db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `BUY_MARK` | numeric | có dữ liệu |
| `db2:pmcrdiss` | `BUY_MARK` | numeric | có dữ liệu |
| `db2:pmcrdrcv` | `BUY_MARK` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `BUY_MARK` | numeric | có dữ liệu |
| `db2:rdiscinf` | `BUY_MARK` | numeric | có dữ liệu |
| `db2:sku_def` | `BUY_MARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdiss.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdrcv.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdstk.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:rdiscinf.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:sku_def.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Phát sinh mua/tích: BUY_MARK
