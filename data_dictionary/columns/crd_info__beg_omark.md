---
semantic_key: crd_info__beg_omark
title: crd info · beg omark
display_names:
- BEG_OMARK
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_OMARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_OMARK'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_OMARK
- 'db2:crd_info.BEG_OMARK: top=0(999), 150(1)'
---

# crd info · beg omark

**Semantic key:** `crd_info__beg_omark` · **Cột vật lý:** `BEG_OMARK`

## Ý nghĩa nghiệp vụ

Cột BEG_OMARK trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `BEG_OMARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.BEG_OMARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_OMARK
