---
semantic_key: hisrtpr__surp_pc
title: hisrtpr · surp pc
display_names:
- SURP_PC
kind: measure
tables:
- ref: db2:hisrtpr
  column: SURP_PC
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột SURP_PC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SURP_PC
- 'db2:hisrtpr.SURP_PC: top=0.00(1000)'
---

# hisrtpr · surp pc

**Semantic key:** `hisrtpr__surp_pc` · **Cột vật lý:** `SURP_PC`

## Ý nghĩa nghiệp vụ

Cột SURP_PC trên HISRTPR. db2:hisrtpr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hisrtpr` | `SURP_PC` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hisrtpr.SURP_PC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

