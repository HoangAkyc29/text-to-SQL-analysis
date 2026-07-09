---
semantic_key: account__y_credit
title: account · y credit
display_names:
- Y_CREDIT
kind: measure
tables:
- ref: db2:account
  column: Y_CREDIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột Y_CREDIT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for Y_CREDIT
- 'db2:account.Y_CREDIT: top=0.00(170), 3213000.00(2), 1320000.00(2), 6480000.00(2),
  28970000.00(1)'
---

# account · y credit

**Semantic key:** `account__y_credit` · **Cột vật lý:** `Y_CREDIT`

## Ý nghĩa nghiệp vụ

Cột Y_CREDIT trên ACCOUNT. db2:account: top 79630135.09, 225977491.03, 1752592158.12.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `Y_CREDIT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.Y_CREDIT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `79630135.09`×1, `225977491.03`×1, `1752592158.12`×1, `0.00`×1, `94821158.26`×1, `17548275518.71`×1, `732309463.50`×1, `2873362895.22`×1

## Ghi chú thêm

