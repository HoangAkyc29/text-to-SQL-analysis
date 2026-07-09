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
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crd_info.BUY_AMT: top=0(184), 195000(2), 245000(2), 84000(2), 10637818(1)'
---

# Tổng doanh thu mua tích điểm lifetime (CRD_INFO.BUY_AMT)

**Semantic key:** `loyalty_lifetime_purchase_amount` · **Cột vật lý:** `BUY_AMT`

## Ý nghĩa nghiệp vụ

CRD_INFO.BUY_AMT — tổng doanh thu mua đã tích điểm lifetime. Sample: 1M–5.9M VND.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BUY_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BUY_AMT`
- Null rate trong sample: 0%
- Distinct ≈19; top: `0`×2, `1092800`×1, `5906050`×1, `4194160`×1, `1600940`×1, `63812`×1, `228008`×1, `174000`×1

## Ghi chú thêm

- Phát sinh mua/tích: BUY_AMT
