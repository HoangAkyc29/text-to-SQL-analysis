---
semantic_key: daily_report_sku_id
title: Mã sản phẩm nội bộ (join master SKU) (SKU_ID)
display_names:
- sku_id
kind: identifier
tables:
- ref: db2:webrpt_sales_sku_daily
  column: sku_id
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã SKU
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã sản phẩm nội bộ (join master SKU) (SKU_ID)

**Semantic key:** `daily_report_sku_id` · **Cột vật lý:** `sku_id`

## Ý nghĩa nghiệp vụ

Mã SKU trên báo cáo doanh số/tồn theo ngày — join SKU_DEF. (bảng WEBRPT_SALES_SKU_DAILY).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `sku_id` | varchar | Mã SKU |

## Join

Thường join: `TRANS_NUM`
