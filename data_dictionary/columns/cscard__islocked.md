---
semantic_key: cscard__islocked
title: cscard · islocked
display_names:
- ISLOCKED
kind: flag
tables:
- ref: db2:cscard
  column: ISLOCKED
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột ISLOCKED
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ISLOCKED
- 'db2:cscard.ISLOCKED: top=False(1000)'
---

# cscard · islocked

**Semantic key:** `cscard__islocked` · **Cột vật lý:** `ISLOCKED`

## Ý nghĩa nghiệp vụ

Cột ISLOCKED trên CSCARD. db2:cscard: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `ISLOCKED` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.ISLOCKED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

