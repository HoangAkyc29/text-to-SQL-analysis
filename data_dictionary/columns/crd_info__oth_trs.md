---
semantic_key: crd_info__oth_trs
title: crd info · oth trs
display_names:
- OTH_TRS
kind: measure
tables:
- ref: db2:crd_info
  column: OTH_TRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh khác: OTH_TRS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for OTH_TRS
- 'db2:crd_info.OTH_TRS: top=0(1000)'
---

# crd info · oth trs

**Semantic key:** `crd_info__oth_trs` · **Cột vật lý:** `OTH_TRS`

## Ý nghĩa nghiệp vụ

Cột OTH_TRS trên CRD_INFO. db2:crd_info: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `OTH_TRS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.OTH_TRS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Phát sinh khác: OTH_TRS
