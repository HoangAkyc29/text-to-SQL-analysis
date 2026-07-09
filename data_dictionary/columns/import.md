---
semantic_key: import
title: import
display_names:
- IMPORT
kind: flag
tables:
- ref: db1:strans
  column: IMPORT
  type: bit
- ref: db2:asso_inf
  column: IMPORT
  type: bit
- ref: db2:custhist
  column: IMPORT
  type: bit
- ref: db2:st_order
  column: IMPORT
  type: bit
- ref: db2:strans
  column: IMPORT
  type: bit
- ref: db2:strans_tmp
  column: IMPORT
  type: bit
- ref: db2:suspend
  column: IMPORT
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cờ nhập / import
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.IMPORT: top=False(860), True(140)'
- 'db2:asso_inf.IMPORT: top=False(512), True(488)'
- 'db2:custhist.IMPORT: top=True(884), False(116)'
- 'db2:st_order.IMPORT: top=False(1000)'
- 'db2:strans.IMPORT: top=False(947), True(53)'
- 'db2:strans_tmp.IMPORT: top=False(999), True(1)'
- 'db2:suspend.IMPORT: top=False(1000)'
---

# import

**Semantic key:** `import` · **Cột vật lý:** `IMPORT`

## Ý nghĩa nghiệp vụ

Cột IMPORT trên ASSO_INF, CUSTHIST, STRANS. db1:strans: top True; db2:asso_inf: top False, True; db2:custhist: top True; db2:st_order: top False; db2:strans: top True; db2:strans_tmp: top False; db2:suspend: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `IMPORT` | bit | có dữ liệu |
| `db2:asso_inf` | `IMPORT` | bit | có dữ liệu |
| `db2:custhist` | `IMPORT` | bit | có dữ liệu |
| `db2:st_order` | `IMPORT` | bit | có dữ liệu |
| `db2:strans` | `IMPORT` | bit | có dữ liệu |
| `db2:strans_tmp` | `IMPORT` | bit | có dữ liệu |
| `db2:suspend` | `IMPORT` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:asso_inf.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×10, `True`×10

### `db2:custhist.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:st_order.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:strans.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:strans_tmp.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:suspend.IMPORT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cờ nhập / import
