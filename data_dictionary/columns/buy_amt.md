---
semantic_key: buy_amt
title: buy amt
display_names:
- BUY_AMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: BUY_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:rdiscinf.BUY_AMT: top=0(1000)'
---

# buy amt

**Semantic key:** `buy_amt` · **Cột vật lý:** `BUY_AMT`

## Ý nghĩa nghiệp vụ

Cột BUY_AMT trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `BUY_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.BUY_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Phát sinh mua/tích: BUY_AMT
