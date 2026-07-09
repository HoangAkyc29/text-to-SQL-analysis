---
semantic_key: account__y_debit
title: account · y debit
display_names:
- Y_DEBIT
kind: measure
tables:
- ref: db2:account
  column: Y_DEBIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột Y_DEBIT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for Y_DEBIT
- 'db2:account.Y_DEBIT: top=0.00(546), 30000.00(2), 230000.00(2), 3167049.00(1), 2880000.00(1)'
---

# account · y debit

**Semantic key:** `account__y_debit` · **Cột vật lý:** `Y_DEBIT`

## Ý nghĩa nghiệp vụ

Cột Y_DEBIT trên ACCOUNT. db2:account: top 0.00, 4707107.50, 29286820.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `Y_DEBIT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.Y_DEBIT`
- Null rate trong sample: 0%
- Distinct ≈16; top: `0.00`×5, `4707107.50`×1, `29286820.00`×1, `20293670.00`×1, `77891388.69`×1, `5527119.95`×1, `7208095.20`×1, `2068516.10`×1

## Ghi chú thêm

