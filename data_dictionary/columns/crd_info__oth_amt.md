---
semantic_key: crd_info__oth_amt
title: crd info · oth amt
display_names:
- OTH_AMT
kind: measure
tables:
- ref: db2:crd_info
  column: OTH_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh khác: OTH_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for OTH_AMT
- 'db2:crd_info.OTH_AMT: top=0(846), 7500000(23), -12500000(10), -10000000(10), -25000000(7)'
---

# crd info · oth amt

**Semantic key:** `crd_info__oth_amt` · **Cột vật lý:** `OTH_AMT`

## Ý nghĩa nghiệp vụ

Cột OTH_AMT trên CRD_INFO. db2:crd_info: top 0, -16900000, -4100000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `OTH_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.OTH_AMT`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0`×18, `-16900000`×1, `-4100000`×1

## Ghi chú thêm

- Phát sinh khác: OTH_AMT
