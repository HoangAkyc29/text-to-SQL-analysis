---
semantic_key: sku_def__rc_type
title: sku def · rc type
display_names:
- RC_TYPE
kind: text
tables:
- ref: db2:sku_def
  column: RC_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột RC_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RC_TYPE
- 'db2:sku_def.RC_TYPE: top=0(2), 1(2)'
---

# sku def · rc type

**Semantic key:** `sku_def__rc_type` · **Cột vật lý:** `RC_TYPE`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `RC_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột RC_TYPE
