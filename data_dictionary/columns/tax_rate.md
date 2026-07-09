---
semantic_key: tax_rate
title: tax rate
display_names:
- TAX_RATE
kind: measure
tables:
- ref: db2:asso_inf
  column: TAX_RATE
  type: numeric
- ref: db2:ctrans
  column: TAX_RATE
  type: numeric
- ref: db2:sku_def
  column: TAX_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Thuế suất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.TAX_RATE: top=0.00(431), 8.00(293), 5.00(265), 10.00(11)'
- 'db2:ctrans.TAX_RATE: top=8.00(489), 0.00(383), 10.00(28), 5.00(25), 3.38(2)'
- 'db2:sku_def.TAX_RATE: top=0.00(596), 8.00(330), 5.00(68), 10.00(6)'
---

# tax rate

**Semantic key:** `tax_rate` · **Cột vật lý:** `TAX_RATE`

## Ý nghĩa nghiệp vụ

Cột TAX_RATE trên ASSO_INF, CTRANS, SKU_DEF. db2:asso_inf: top 0.00, 8.00; db2:ctrans: top 8.00, 0.00, 1.81; db2:sku_def: top 0.00, 8.00, 5.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `TAX_RATE` | numeric | có dữ liệu |
| `db2:ctrans` | `TAX_RATE` | numeric | có dữ liệu |
| `db2:sku_def` | `TAX_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.TAX_RATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.00`×18, `8.00`×2

### `db2:ctrans.TAX_RATE`
- Null rate trong sample: 0%
- Distinct ≈6; top: `8.00`×9, `0.00`×7, `1.81`×1, `3.65`×1, `1.62`×1, `3.58`×1

### `db2:sku_def.TAX_RATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0.00`×15, `8.00`×3, `5.00`×2

## Ghi chú thêm

- Thuế suất
