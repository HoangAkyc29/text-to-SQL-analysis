---
semantic_key: crd_info__beg_bamt
title: crd info · beg bamt
display_names:
- BEG_BAMT
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_BAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_BAMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_BAMT
- 'db2:crd_info.BEG_BAMT: top=0(998), 3057750(1), 175349(1)'
---

# crd info · beg bamt

**Semantic key:** `crd_info__beg_bamt` · **Cột vật lý:** `BEG_BAMT`

## Ý nghĩa nghiệp vụ

Cột BEG_BAMT trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_BAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_BAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_BAMT
