---
semantic_key: rdiscinf__sold_qty
title: rdiscinf · sold qty
display_names:
- SOLD_QTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: SOLD_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngSOLD_QTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SOLD_QTY
- 'db2:rdiscinf.SOLD_QTY: top=1.000(977), 0.000(21), 2.000(1), 100.000(1)'
---

# rdiscinf · sold qty

**Semantic key:** `rdiscinf__sold_qty` · **Cột vật lý:** `SOLD_QTY`

## Ý nghĩa nghiệp vụ

Cột SOLD_QTY trên RDISCINF. db2:rdiscinf: top 0.010, 1.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `SOLD_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.SOLD_QTY`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.010`×17, `1.000`×3

## Ghi chú thêm

- Số lượngSOLD_QTY
