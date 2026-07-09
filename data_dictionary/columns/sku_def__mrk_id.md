---
semantic_key: sku_def__mrk_id
title: sku def · mrk id
display_names:
- MRK_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: MRK_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột MRK_ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MRK_ID
- 'db2:sku_def.MRK_ID: top=0000(724)'
---

# sku def · mrk id

**Semantic key:** `sku_def__mrk_id` · **Cột vật lý:** `MRK_ID`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `MRK_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột MRK_ID
