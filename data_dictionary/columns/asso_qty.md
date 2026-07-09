---
semantic_key: asso_qty
title: asso qty
display_names:
- ASSO_QTY
kind: measure
tables:
- ref: db1:strans
  column: ASSO_QTY
  type: numeric
- ref: db2:strans
  column: ASSO_QTY
  type: numeric
- ref: db2:strans_tmp
  column: ASSO_QTY
  type: numeric
- ref: db2:suspend
  column: ASSO_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng trong combo
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.ASSO_QTY: top=0.000(999), 1.000(1)'
- 'db2:strans.ASSO_QTY: top=0.000(998), 1.000(2)'
- 'db2:strans_tmp.ASSO_QTY: top=0.000(1000)'
- 'db2:suspend.ASSO_QTY: top=0.000(1000)'
---

# asso qty

**Semantic key:** `asso_qty` · **Cột vật lý:** `ASSO_QTY`

## Ý nghĩa nghiệp vụ

Cột ASSO_QTY trên STRANS, STRANS_TMP, SUSPEND. db1:strans: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `ASSO_QTY` | numeric | có dữ liệu |
| `db2:strans` | `ASSO_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `ASSO_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `ASSO_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.ASSO_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.ASSO_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.ASSO_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.ASSO_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượng trong combo
