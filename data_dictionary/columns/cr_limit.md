---
semantic_key: cr_limit
title: cr limit
display_names:
- CR_LIMIT
kind: measure
tables:
- ref: db2:account
  column: CR_LIMIT
  type: numeric
- ref: db2:partner
  column: CR_LIMIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Hạn mức tín dụng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:account.CR_LIMIT: top=0.00(1000)'
- 'db2:partner.CR_LIMIT: top=0.00(999), 1000000000.00(1)'
---

# cr limit

**Semantic key:** `cr_limit` · **Cột vật lý:** `CR_LIMIT`

## Ý nghĩa nghiệp vụ

Cột CR_LIMIT trên ACCOUNT, PARTNER. db2:account: top 0.00; db2:partner: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `CR_LIMIT` | numeric | có dữ liệu |
| `db2:partner` | `CR_LIMIT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.CR_LIMIT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:partner.CR_LIMIT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hạn mức tín dụng
