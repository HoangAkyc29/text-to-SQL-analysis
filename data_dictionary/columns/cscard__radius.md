---
semantic_key: cscard__radius
title: cscard · radius
display_names:
- RADIUS
kind: measure
tables:
- ref: db2:cscard
  column: RADIUS
  type: int
join_with: []
related_semantic_keys: []
facts:
- Cột RADIUS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RADIUS
- 'db2:cscard.RADIUS: min=0.0 max=0.0'
---

# cscard · radius

**Semantic key:** `cscard__radius` · **Cột vật lý:** `RADIUS`

## Ý nghĩa nghiệp vụ

Cột RADIUS trên CSCARD. db2:cscard: 0.0…0.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `RADIUS` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.RADIUS`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

## Ghi chú thêm

