---
semantic_key: partner__payday
title: partner · payday
display_names:
- PAYDAY
kind: measure
tables:
- ref: db2:partner
  column: PAYDAY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột PAYDAY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PAYDAY
- 'db2:partner.PAYDAY: top=0(1000)'
---

# partner · payday

**Semantic key:** `partner__payday` · **Cột vật lý:** `PAYDAY`

## Ý nghĩa nghiệp vụ

Cột PAYDAY trên PARTNER. db2:partner: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `PAYDAY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.PAYDAY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

