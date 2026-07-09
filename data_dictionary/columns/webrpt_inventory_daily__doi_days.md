---
semantic_key: webrpt_inventory_daily__doi_days
title: webrpt inventory daily · doi days
display_names:
- doi_days
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: doi_days
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Days of inventory
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for doi_days
- 'db2:webrpt_inventory_daily.doi_days: top=915.0(1), 485.3(1), 0.0(1)'
---

# webrpt inventory daily · doi days

**Semantic key:** `webrpt_inventory_daily__doi_days` · **Cột vật lý:** `doi_days`

## Ý nghĩa nghiệp vụ

Days of inventory

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `doi_days` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

