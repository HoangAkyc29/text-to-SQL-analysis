---
semantic_key: hisrtpr__rtpramt
title: hisrtpr · rtpramt
display_names:
- RTPRAMT
kind: measure
tables:
- ref: db2:hisrtpr
  column: RTPRAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột RTPRAMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RTPRAMT
- 'db2:hisrtpr.RTPRAMT: top=0.00(1000)'
---

# hisrtpr · rtpramt

**Semantic key:** `hisrtpr__rtpramt` · **Cột vật lý:** `RTPRAMT`

## Ý nghĩa nghiệp vụ

Cột RTPRAMT trên HISRTPR. db2:hisrtpr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hisrtpr` | `RTPRAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hisrtpr.RTPRAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

