---
semantic_key: webrpt_inventory_daily__days_since_receipt
title: webrpt inventory daily · days since receipt
display_names:
- days_since_receipt
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: days_since_receipt
  type: int
join_with: []
related_semantic_keys: []
facts:
- Cột days_since_receipt
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for days_since_receipt
- 'db2:webrpt_inventory_daily.days_since_receipt: min=14.0 max=900.0'
---

# webrpt inventory daily · days since receipt

**Semantic key:** `webrpt_inventory_daily__days_since_receipt` · **Cột vật lý:** `days_since_receipt`

## Ý nghĩa nghiệp vụ

Cột DAYS_SINCE_RECEIPT trên WEBRPT_INVENTORY_DAILY. db2:webrpt_inventory_daily: 4.0…550.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `days_since_receipt` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.days_since_receipt`
- Null rate trong sample: 75%
- Numeric range: 4.0 … 550.0
- Ví dụ: 538, 4, 116, 550, 550

## Ghi chú thêm

- Cột days_since_receipt
