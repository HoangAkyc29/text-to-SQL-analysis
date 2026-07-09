---
semantic_key: cscard__bonus_pc
title: cscard · bonus pc
display_names:
- BONUS_PC
kind: measure
tables:
- ref: db2:cscard
  column: BONUS_PC
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Phần trăm thưởng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BONUS_PC
- 'db2:cscard.BONUS_PC: top=0.00(1000)'
---

# cscard · bonus pc

**Semantic key:** `cscard__bonus_pc` · **Cột vật lý:** `BONUS_PC`

## Ý nghĩa nghiệp vụ

Cột BONUS_PC trên CSCARD. db2:cscard: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `BONUS_PC` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.BONUS_PC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Phần trăm thưởng
