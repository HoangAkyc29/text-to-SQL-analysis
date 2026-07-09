---
semantic_key: report_date
title: report date
display_names:
- report_date
kind: date
tables:
- ref: db2:webrpt_inventory_daily
  column: report_date
  type: date
- ref: db2:webrpt_sales_sku_daily
  column: report_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày báo cáo
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_inventory_daily.report_date: top=2026-07-06(28), 2026-05-30(23), 2026-05-22(21),
  2026-06-27(20), 2026-05-23(19)'
- 'db2:webrpt_sales_sku_daily.report_date: top=2026-04-01(512), 2026-04-02(488)'
---

# report date

**Semantic key:** `report_date` · **Cột vật lý:** `report_date`

## Ý nghĩa nghiệp vụ

Cột REPORT_DATE trên WEBRPT_INVENTORY_DAILY, WEBRPT_SALES_SKU_DAILY. db2:webrpt_inventory_daily: top 2026-04-02; db2:webrpt_sales_sku_daily: top 2026-04-01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `report_date` | date | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `report_date` | date | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.report_date`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-02`×20

### `db2:webrpt_sales_sku_daily.report_date`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-01`×20

## Ghi chú thêm

- Ngày báo cáo
