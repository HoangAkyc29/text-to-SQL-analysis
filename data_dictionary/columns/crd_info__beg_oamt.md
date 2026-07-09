---
semantic_key: crd_info__beg_oamt
title: crd info · beg oamt
display_names:
- BEG_OAMT
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_OAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_OAMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_OAMT
- 'db2:crd_info.BEG_OAMT: top=0(999), 7500000(1)'
---

# crd info · beg oamt

**Semantic key:** `crd_info__beg_oamt` · **Cột vật lý:** `BEG_OAMT`

## Ý nghĩa nghiệp vụ

Cột BEG_OAMT trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_OAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_OAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_OAMT
