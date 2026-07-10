---
semantic_key: webrpt_inventory_daily__avg_daily_qty_30d
title: Avg Daily Qty 30D (WEBRPT_INVENTORY_DAILY)
display_names:
- avg_daily_qty_30d
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: avg_daily_qty_30d
  type: decimal
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Avg Daily Qty 30D (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__avg_daily_qty_30d` · **Cột vật lý:** `avg_daily_qty_30d`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `avg_daily_qty_30d` | decimal | Chỉ số đo lường (avg daily qty 30d) trên bảng webrpt_inventory_daily |
