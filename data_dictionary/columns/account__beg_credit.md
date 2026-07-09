---
semantic_key: account__beg_credit
title: account · beg credit
display_names:
- BEG_CREDIT
kind: measure
tables:
- ref: db2:account
  column: BEG_CREDIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_CREDIT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEG_CREDIT
- 'db2:account.BEG_CREDIT: top=0.00(1000)'
---

# account · beg credit

**Semantic key:** `account__beg_credit` · **Cột vật lý:** `BEG_CREDIT`

## Ý nghĩa nghiệp vụ

Cột BEG_CREDIT trên ACCOUNT. db2:account: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `BEG_CREDIT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.BEG_CREDIT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số dư đầu kỳ: BEG_CREDIT
