---
semantic_key: loyalty_lifetime_purchase_amount
title: Tổng doanh thu mua tích điểm lifetime (CRD_INFO.BUY_AMT)
display_names:
- BUY_AMT
kind: measure
tables:
- ref: db2:crd_info
  column: BUY_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tổng doanh thu mua tích điểm lifetime (CRD_INFO.BUY_AMT)

**Semantic key:** `loyalty_lifetime_purchase_amount` · **Cột vật lý:** `BUY_AMT`

## Ý nghĩa nghiệp vụ

Tổng doanh thu mua đã tích điểm lifetime (CRD_INFO.BUY_AMT).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `BUY_AMT` | numeric | Phát sinh mua/tích: BUY_AMT |

## Ghi chú thêm

- Phát sinh mua/tích: BUY_AMT
