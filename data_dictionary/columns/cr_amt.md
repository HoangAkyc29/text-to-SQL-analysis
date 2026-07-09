---
semantic_key: cr_amt
title: cr amt
display_names:
- CR_AMT
kind: measure
tables:
- ref: db2:account
  column: CR_AMT
  type: numeric
- ref: db2:partner
  column: CR_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Dư nợ hiện tại
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:account.CR_AMT: top=0.00(1000)'
- 'db2:partner.CR_AMT: top=0.00(1000)'
---

# cr amt

**Semantic key:** `cr_amt` · **Cột vật lý:** `CR_AMT`

## Ý nghĩa nghiệp vụ

Cột CR_AMT trên ACCOUNT, PARTNER. db2:account: top 0.00; db2:partner: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `CR_AMT` | numeric | có dữ liệu |
| `db2:partner` | `CR_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.CR_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:partner.CR_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Dư nợ hiện tại
