---
semantic_key: sku_def__unit_desc
title: sku def · unit desc
display_names:
- UNIT_DESC
kind: text
tables:
- ref: db2:sku_def
  column: UNIT_DESC
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột UNIT_DESC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for UNIT_DESC
- 'db2:sku_def.UNIT_DESC: top=C¸i(518), Hép(91), Khay(79), Gãi(78), Chai(48)'
---

# sku def · unit desc

**Semantic key:** `sku_def__unit_desc` · **Cột vật lý:** `UNIT_DESC`

## Ý nghĩa nghiệp vụ

Cột UNIT_DESC trên SKU_DEF. db2:sku_def: top C¸i, Khay, Bao.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `UNIT_DESC` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.UNIT_DESC`
- Null rate trong sample: 0%
- Distinct ≈5; top: `C¸i`×12, `Khay`×5, `Bao`×1, `Hép`×1, `KG`×1

## Ghi chú thêm

