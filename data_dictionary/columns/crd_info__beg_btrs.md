---
semantic_key: crd_info__beg_btrs
title: crd info · beg btrs
display_names:
- BEG_BTRS
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_BTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_BTRS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_BTRS
- 'db2:crd_info.BEG_BTRS: top=0(1000)'
---

# crd info · beg btrs

**Semantic key:** `crd_info__beg_btrs` · **Cột vật lý:** `BEG_BTRS`

## Ý nghĩa nghiệp vụ

Cột BEG_BTRS trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_BTRS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_BTRS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_BTRS
