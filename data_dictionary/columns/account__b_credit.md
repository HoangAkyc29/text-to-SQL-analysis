---
semantic_key: account__b_credit
title: account · b credit
display_names:
- B_CREDIT
kind: measure
tables:
- ref: db2:account
  column: B_CREDIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột B_CREDIT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for B_CREDIT
- 'db2:account.B_CREDIT: top=0.00(193), 71280000.00(3), 307360000.00(1), 115780879.40(1),
  17850001.26(1)'
---

# account · b credit

**Semantic key:** `account__b_credit` · **Cột vật lý:** `B_CREDIT`

## Ý nghĩa nghiệp vụ

Cột B_CREDIT trên ACCOUNT. db2:account: top 877745396.53, 2463048589.74, 18655664842.08.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `B_CREDIT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.B_CREDIT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `877745396.53`×1, `2463048589.74`×1, `18655664842.08`×1, `0.00`×1, `832823409.82`×1, `144159291291.33`×1, `6631803964.97`×1, `15915088066.38`×1

## Ghi chú thêm

