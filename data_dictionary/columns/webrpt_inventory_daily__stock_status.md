---
semantic_key: webrpt_inventory_daily__stock_status
title: Stock Status (WEBRPT_INVENTORY_DAILY)
display_names:
- stock_status
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: stock_status
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Stock Status (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__stock_status` · **Cột vật lý:** `stock_status`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `stock_status` | varchar | Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …) |

## Ghi chú thêm

- Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …)
