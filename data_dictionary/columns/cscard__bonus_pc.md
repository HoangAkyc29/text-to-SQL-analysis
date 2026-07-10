---
semantic_key: cscard__bonus_pc
title: Bonus Pc (CSCARD)
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
- column_semantic_registry
- business_prose
---

# Bonus Pc (CSCARD)

**Semantic key:** `cscard__bonus_pc` · **Cột vật lý:** `BONUS_PC`

## Ý nghĩa nghiệp vụ

Tỷ lệ thưởng điểm bonus (%) so với tích chuẩn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `BONUS_PC` | numeric | Phần trăm thưởng |

## Ghi chú thêm

- Phần trăm thưởng
