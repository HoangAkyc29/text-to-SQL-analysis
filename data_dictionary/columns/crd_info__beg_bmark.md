---
semantic_key: crd_info__beg_bmark
title: crd info · beg bmark
display_names:
- BEG_BMARK
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_BMARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_BMARK'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_BMARK
- 'db2:crd_info.BEG_BMARK: top=0(998), 59(1), 3(1)'
---

# crd info · beg bmark

**Semantic key:** `crd_info__beg_bmark` · **Cột vật lý:** `BEG_BMARK`

## Ý nghĩa nghiệp vụ

Cột BEG_BMARK trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_BMARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_BMARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_BMARK
