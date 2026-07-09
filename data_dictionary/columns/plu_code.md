---
semantic_key: plu_code
title: plu code
display_names:
- PLU_CODE
kind: code
tables:
- ref: db2:asso_inf
  column: PLU_CODE
  type: char
- ref: db2:plu
  column: PLU_CODE
  type: varchar
- ref: db2:sku_def
  column: PLU_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã PLU
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.PLU_CODE: top=0648(6), 2559(5), 0427(5), 4494(5), 3388(5)'
- 'db2:plu.PLU_CODE: top=0063(1), 0501(1), 2840(1), 0214(1), 5117(1)'
- 'db2:sku_def.PLU_CODE: top=0894(1), 4160(1), 4348(1), 0522(1), 3292(1)'
---

# plu code

**Semantic key:** `plu_code` · **Cột vật lý:** `PLU_CODE`

## Ý nghĩa nghiệp vụ

Cột PLU_CODE trên ASSO_INF, PLU, SKU_DEF. db2:asso_inf: top 0510, 0078, 3044; db2:plu: top 0001, 0002, 0003; db2:sku_def: top 3156.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `PLU_CODE` | char | có dữ liệu |
| `db2:plu` | `PLU_CODE` | varchar | có dữ liệu |
| `db2:sku_def` | `PLU_CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.PLU_CODE`
- Null rate trong sample: 85%
- Distinct ≈3; top: `0510`×1, `0078`×1, `3044`×1

### `db2:plu.PLU_CODE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `0001`×1, `0002`×1, `0003`×1, `0004`×1, `0005`×1, `0006`×1, `0007`×1, `0008`×1

### `db2:sku_def.PLU_CODE`
- Null rate trong sample: 95%
- Distinct ≈1; top: `3156`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã PLU
