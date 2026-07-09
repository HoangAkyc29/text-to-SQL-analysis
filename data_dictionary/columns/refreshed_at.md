---
semantic_key: refreshed_at
title: refreshed at
display_names:
- refreshed_at
kind: date
tables:
- ref: db2:webrpt_inventory_daily
  column: refreshed_at
  type: datetime
- ref: db2:webrpt_rfm_snapshot
  column: refreshed_at
  type: datetime
- ref: db2:webrpt_sales_sku_daily
  column: refreshed_at
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Thời điểm làm mới báo cáo
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_inventory_daily.refreshed_at: top=2026-07-06 02:20:00.527000(28), 2026-05-30
  02:20:00.353000(23), 2026-05-22 02:20:00.960000(21), 2026-06-27 02:20:00.787000(20),
  2026-05-23 02:20:00.760000(19)'
- 'db2:webrpt_rfm_snapshot.refreshed_at: top=2026-04-01 11:50:25.717000(1000)'
- 'db2:webrpt_sales_sku_daily.refreshed_at: top=2026-04-02 13:22:38.377000(512), 2026-04-03
  13:17:38.523000(488)'
---

# refreshed at

**Semantic key:** `refreshed_at` · **Cột vật lý:** `refreshed_at`

## Ý nghĩa nghiệp vụ

Cột REFRESHED_AT trên WEBRPT_INVENTORY_DAILY, WEBRPT_RFM_SNAPSHOT, WEBRPT_SALES_SKU_DAILY. db2:webrpt_inventory_daily: top 2026-04-03T13:41:57.720000; db2:webrpt_rfm_snapshot: top 2026-04-01T11:50:25.717000; db2:webrpt_sales_sku_daily: top 2026-04-02T13:22:38.377000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `refreshed_at` | datetime | có dữ liệu |
| `db2:webrpt_rfm_snapshot` | `refreshed_at` | datetime | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `refreshed_at` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.refreshed_at`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-03T13:41:57.720000`×20

### `db2:webrpt_rfm_snapshot.refreshed_at`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-01T11:50:25.717000`×20

### `db2:webrpt_sales_sku_daily.refreshed_at`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-02T13:22:38.377000`×20

## Ghi chú thêm

- Thời điểm làm mới báo cáo
