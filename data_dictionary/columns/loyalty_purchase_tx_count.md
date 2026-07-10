---
semantic_key: loyalty_purchase_tx_count
title: Số lần phát sinh mua tích điểm (CRD_INFO.BUY_TRS)
display_names:
- BUY_TRS
kind: measure
tables:
- ref: db2:crd_info
  column: BUY_TRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_TRS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lần phát sinh mua tích điểm (CRD_INFO.BUY_TRS)

**Semantic key:** `loyalty_purchase_tx_count` · **Cột vật lý:** `BUY_TRS`

## Ý nghĩa nghiệp vụ

Số lần phát sinh mua được tính vào tích điểm (CRD_INFO.BUY_TRS). Là số lượng giao dịch, không phải số tiền.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `BUY_TRS` | numeric | Phát sinh mua/tích: BUY_TRS |

## Ghi chú thêm

- Phát sinh mua/tích: BUY_TRS
