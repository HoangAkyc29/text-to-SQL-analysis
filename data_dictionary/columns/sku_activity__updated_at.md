---
semantic_key: sku_activity__updated_at
title: Updated At (SKU_ACTIVITY)
display_names:
- updated_at
kind: date
tables:
- ref: db2:sku_activity
  column: updated_at
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Thời điểm cập nhật
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Updated At (SKU_ACTIVITY)

**Semantic key:** `sku_activity__updated_at` · **Cột vật lý:** `updated_at`

## Ý nghĩa nghiệp vụ

Mốc thời gian (updated at) — bảng SKU_ACTIVITY.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_activity` | `updated_at` | datetime | Thời điểm cập nhật |

## Ghi chú thêm

- Thời điểm cập nhật
