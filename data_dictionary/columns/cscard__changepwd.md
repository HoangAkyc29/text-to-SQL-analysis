---
semantic_key: cscard__changepwd
title: cscard · changepwd
display_names:
- CHANGEPWD
kind: flag
tables:
- ref: db2:cscard
  column: CHANGEPWD
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột CHANGEPWD
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CHANGEPWD
- 'db2:cscard.CHANGEPWD: top=False(1000)'
---

# cscard · changepwd

**Semantic key:** `cscard__changepwd` · **Cột vật lý:** `CHANGEPWD`

## Ý nghĩa nghiệp vụ

Cột CHANGEPWD trên CSCARD. db2:cscard: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `CHANGEPWD` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.CHANGEPWD`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

