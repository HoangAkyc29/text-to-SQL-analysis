---
semantic_key: cash_denomination_value
title: cash denomination value
display_names:
- VALUE
kind: measure
tables:
- ref: db2:cash_st
  column: VALUE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Mệnh giá tờ tiền (200, 500, 1000, … VND)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cash_st.VALUE: top=500000(194), 200000(157), 100000(118), 10000(102), 50000(91)'
---

# cash denomination value

**Semantic key:** `cash_denomination_value` · **Cột vật lý:** `VALUE`

## Ý nghĩa nghiệp vụ

Cột VALUE trên CASH_ST. db2:cash_st: top 200, 500, 1000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cash_st` | `VALUE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cash_st.VALUE`
- Null rate trong sample: 0%
- Distinct ≈11; top: `200`×2, `500`×2, `1000`×2, `2000`×2, `5000`×2, `10000`×2, `20000`×2, `50000`×2

## Ghi chú thêm

- Mệnh giá tờ tiền (200, 500, 1000, … VND)
