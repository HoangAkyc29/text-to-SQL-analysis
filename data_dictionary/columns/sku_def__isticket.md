---
semantic_key: sku_def__isticket
title: sku def · isticket
display_names:
- IsTicket
kind: flag
tables:
- ref: db2:sku_def
  column: IsTicket
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsTicket
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsTicket
- 'db2:sku_def.IsTicket: top=False(1000)'
---

# sku def · isticket

**Semantic key:** `sku_def__isticket` · **Cột vật lý:** `IsTicket`

## Ý nghĩa nghiệp vụ

Cột ISTICKET trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsTicket` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsTicket`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsTicket
