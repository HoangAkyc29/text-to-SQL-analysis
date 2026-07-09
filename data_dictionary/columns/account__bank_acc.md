---
semantic_key: account__bank_acc
title: account · bank acc
display_names:
- BANK_ACC
kind: flag
tables:
- ref: db2:account
  column: BANK_ACC
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột BANK_ACC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BANK_ACC
- 'db2:account.BANK_ACC: top=False(1000)'
---

# account · bank acc

**Semantic key:** `account__bank_acc` · **Cột vật lý:** `BANK_ACC`

## Ý nghĩa nghiệp vụ

Cột BANK_ACC trên ACCOUNT. db2:account: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `BANK_ACC` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.BANK_ACC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

