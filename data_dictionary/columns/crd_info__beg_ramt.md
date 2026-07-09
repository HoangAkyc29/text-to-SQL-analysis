---
semantic_key: crd_info__beg_ramt
title: crd info · beg ramt
display_names:
- BEG_RAMT
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_RAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_RAMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_RAMT
- 'db2:crd_info.BEG_RAMT: top=0(1000)'
---

# crd info · beg ramt

**Semantic key:** `crd_info__beg_ramt` · **Cột vật lý:** `BEG_RAMT`

## Ý nghĩa nghiệp vụ

Cột BEG_RAMT trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_RAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_RAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_RAMT
