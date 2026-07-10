---
semantic_key: barcode__isdefault
title: Cờ thuộc tính (default) (BARCODE)
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
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (default) (BARCODE)

**Semantic key:** `barcode__isdefault` · **Cột vật lý:** `ISDEFAULT`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính (default) — bảng barcode ↔ SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:barcode` | `ISDEFAULT` | bit | Mặc định |

## Ghi chú thêm

- Mặc định
