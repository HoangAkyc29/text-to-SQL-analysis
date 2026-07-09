---
semantic_key: action
title: action
display_names:
- ACTION
kind: text
tables:
- ref: db2:ctrans
  column: ACTION
  type: char
- ref: db2:debt
  column: ACTION
  type: char
- ref: db2:st_order
  column: ACTION
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã thao tác
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:ctrans.ACTION: top=C(958), D(42)'
- 'db2:debt.ACTION: top=C(950), D(50)'
- 'db2:st_order.ACTION: top=8(1000)'
---

# action

**Semantic key:** `action` · **Cột vật lý:** `ACTION`

## Ý nghĩa nghiệp vụ

Cột ACTION trên CTRANS, DEBT, ST_ORDER. db2:ctrans: top C; db2:debt: top C; db2:st_order: top 8.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `ACTION` | char | có dữ liệu |
| `db2:debt` | `ACTION` | char | có dữ liệu |
| `db2:st_order` | `ACTION` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.ACTION`
- Null rate trong sample: 0%
- Distinct ≈1; top: `C`×20

### `db2:debt.ACTION`
- Null rate trong sample: 0%
- Distinct ≈1; top: `C`×20

### `db2:st_order.ACTION`
- Null rate trong sample: 0%
- Distinct ≈1; top: `8`×20

## Ghi chú thêm

- Mã thao tác
