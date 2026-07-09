---
semantic_key: crd_info__beg_otrs
title: crd info · beg otrs
display_names:
- BEG_OTRS
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_OTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_OTRS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_OTRS
- 'db2:crd_info.BEG_OTRS: top=0(1000)'
---

# crd info · beg otrs

**Semantic key:** `crd_info__beg_otrs` · **Cột vật lý:** `BEG_OTRS`

## Ý nghĩa nghiệp vụ

Cột BEG_OTRS trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_OTRS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_OTRS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_OTRS
