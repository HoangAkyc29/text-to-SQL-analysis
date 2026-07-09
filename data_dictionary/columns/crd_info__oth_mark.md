---
semantic_key: crd_info__oth_mark
title: crd info · oth mark
display_names:
- OTH_MARK
kind: measure
tables:
- ref: db2:crd_info
  column: OTH_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh khác: OTH_MARK'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for OTH_MARK
- 'db2:crd_info.OTH_MARK: top=0(846), 150(23), -250(10), -200(10), -500(7)'
---

# crd info · oth mark

**Semantic key:** `crd_info__oth_mark` · **Cột vật lý:** `OTH_MARK`

## Ý nghĩa nghiệp vụ

Cột OTH_MARK trên CRD_INFO. db2:crd_info: top 0, -338, -82.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `OTH_MARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.OTH_MARK`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0`×18, `-338`×1, `-82`×1

## Ghi chú thêm

- Phát sinh khác: OTH_MARK
