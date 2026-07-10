---
semantic_key: webrpt_inventory_daily__days_since_receipt
title: Days Since Receipt (WEBRPT_INVENTORY_DAILY)
display_names:
- days_since_receipt
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: days_since_receipt
  type: int
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Days Since Receipt (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__days_since_receipt` · **Cột vật lý:** `days_since_receipt`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `days_since_receipt` | int | Chỉ số đo lường (days since receipt) trên bảng webrpt_inventory_daily |
