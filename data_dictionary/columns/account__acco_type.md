---
semantic_key: account__acco_type
title: account · acco type
display_names:
- ACCO_TYPE
kind: text
tables:
- ref: db2:account
  column: ACCO_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột ACCO_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ACCO_TYPE
- 'db2:account.ACCO_TYPE: top=02(999), 03(1)'
---

# account · acco type

**Semantic key:** `account__acco_type` · **Cột vật lý:** `ACCO_TYPE`

## Ý nghĩa nghiệp vụ

Cột ACCO_TYPE trên ACCOUNT. db2:account: top 02.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `ACCO_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.ACCO_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `02`×20

## Ghi chú thêm

