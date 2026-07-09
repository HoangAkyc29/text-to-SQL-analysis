---
semantic_key: sku_def__rc_qty
title: sku def · rc qty
display_names:
- RC_QTY
kind: measure
tables:
- ref: db2:sku_def
  column: RC_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngRC_QTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RC_QTY
- 'db2:sku_def.RC_QTY: top=0(982), 1(18)'
---

# sku def · rc qty

**Semantic key:** `sku_def__rc_qty` · **Cột vật lý:** `RC_QTY`

## Ý nghĩa nghiệp vụ

Cột RC_QTY trên SKU_DEF. db2:sku_def: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `RC_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.RC_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số lượngRC_QTY
