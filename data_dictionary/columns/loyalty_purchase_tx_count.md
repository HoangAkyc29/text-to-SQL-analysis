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
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crd_info.BUY_TRS: top=0(184), 1(164), 2(100), 3(59), 5(37)'
---

# Số lần phát sinh mua tích điểm (CRD_INFO.BUY_TRS)

**Semantic key:** `loyalty_purchase_tx_count` · **Cột vật lý:** `BUY_TRS`

## Ý nghĩa nghiệp vụ

CRD_INFO.BUY_TRS — đếm số lần phát sinh mua liên quan tích điểm. Sample: 0–17, phần lớn 1–2. Không phải số tiền.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BUY_TRS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BUY_TRS`
- Null rate trong sample: 0%
- Distinct ≈8; top: `1`×11, `0`×2, `2`×2, `17`×1, `5`×1, `4`×1, `10`×1, `6`×1

## Ghi chú thêm

- Phát sinh mua/tích: BUY_TRS
