---
semantic_key: sku_activity__updated_at
title: sku activity · updated at
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for updated_at
- 'db2:sku_activity.updated_at: top=2026-04-01 04:46:13.540000(725), 2026-04-01 04:58:44.703000(154),
  2026-04-01 04:58:44.783000(121)'
---

# sku activity · updated at

**Semantic key:** `sku_activity__updated_at` · **Cột vật lý:** `updated_at`

## Ý nghĩa nghiệp vụ

Cột UPDATED_AT trên SKU_ACTIVITY. db2:sku_activity: top 2026-04-01T04:46:13.540000, 2026-04-01T04:58:44.783000, 2026-04-01T04:58:44.703000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_activity` | `updated_at` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_activity.updated_at`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-04-01T04:46:13.540000`×15, `2026-04-01T04:58:44.783000`×3, `2026-04-01T04:58:44.703000`×2

## Ghi chú thêm

- Thời điểm cập nhật
