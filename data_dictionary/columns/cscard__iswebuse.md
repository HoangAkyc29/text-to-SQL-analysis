---
semantic_key: cscard__iswebuse
title: cscard · iswebuse
display_names:
- ISWEBUSE
kind: flag
tables:
- ref: db2:cscard
  column: ISWEBUSE
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột ISWEBUSE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ISWEBUSE
- 'db2:cscard.ISWEBUSE: top=False(1000)'
---

# cscard · iswebuse

**Semantic key:** `cscard__iswebuse` · **Cột vật lý:** `ISWEBUSE`

## Ý nghĩa nghiệp vụ

Cột ISWEBUSE trên CSCARD. db2:cscard: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `ISWEBUSE` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.ISWEBUSE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

