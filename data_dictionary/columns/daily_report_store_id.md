---
semantic_key: daily_report_store_id
title: Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)
display_names:
- stk_id
kind: identifier
tables:
- ref: db2:webrpt_sales_sku_daily
  column: stk_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã cửa hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)

**Semantic key:** `daily_report_store_id` · **Cột vật lý:** `stk_id`

## Ý nghĩa nghiệp vụ

Mã cửa hàng trên báo cáo — grain store × SKU × ngày. (bảng WEBRPT_SALES_SKU_DAILY).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `stk_id` | varchar | Mã cửa hàng |
