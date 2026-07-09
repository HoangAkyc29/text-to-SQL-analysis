---
semantic_key: pmcrdiss__disc_pc
title: pmcrdiss · disc pc
display_names:
- DISC_PC
kind: measure
tables:
- ref: db2:pmcrdiss
  column: DISC_PC
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DISC_PC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISC_PC
- 'db2:pmcrdiss.DISC_PC: top=0.00(1000)'
---

# pmcrdiss · disc pc

**Semantic key:** `pmcrdiss__disc_pc` · **Cột vật lý:** `DISC_PC`

## Ý nghĩa nghiệp vụ

Cột DISC_PC trên PMCRDISS. db2:pmcrdiss: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdiss` | `DISC_PC` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdiss.DISC_PC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

