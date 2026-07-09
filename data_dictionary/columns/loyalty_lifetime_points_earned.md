---
semantic_key: loyalty_lifetime_points_earned
title: Tổng điểm tích lifetime (CRD_INFO.BUY_MARK)
display_names:
- BUY_MARK
kind: measure
tables:
- ref: db2:crd_info
  column: BUY_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_MARK'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crd_info.BUY_MARK: top=0(185), 3(32), 1(30), 2(28), 7(25)'
---

# Tổng điểm tích lifetime (CRD_INFO.BUY_MARK)

**Semantic key:** `loyalty_lifetime_points_earned` · **Cột vật lý:** `BUY_MARK`

## Ý nghĩa nghiệp vụ

CRD_INFO.BUY_MARK — tổng điểm đã tích lifetime. Sample: 1–5 điểm phổ biến.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BUY_MARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BUY_MARK`
- Null rate trong sample: 0%
- Distinct ≈16; top: `0`×2, `1`×2, `3`×2, `5`×2, `21`×1, `112`×1, `82`×1, `32`×1

## Ghi chú thêm

- Phát sinh mua/tích: BUY_MARK
