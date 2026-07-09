---
semantic_key: barcode__isdefault
title: barcode · isdefault
display_names:
- ISDEFAULT
kind: flag
tables:
- ref: db2:barcode
  column: ISDEFAULT
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Mặc định
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ISDEFAULT
- 'db2:barcode.ISDEFAULT: top=False(575), True(425)'
---

# barcode · isdefault

**Semantic key:** `barcode__isdefault` · **Cột vật lý:** `ISDEFAULT`

## Ý nghĩa nghiệp vụ

Cột ISDEFAULT trên BARCODE. db2:barcode: top False, True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:barcode` | `ISDEFAULT` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:barcode.ISDEFAULT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×13, `True`×7

## Ghi chú thêm

- Mặc định
