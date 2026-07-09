---
semantic_key: pmt_code
title: pmt code
display_names:
- PMT_CODE
kind: code
tables:
- ref: db2:cash_st
  column: PMT_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- 'Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space)'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cash_st.PMT_CODE: top=CASH(1000)'
---

# pmt code

**Semantic key:** `pmt_code` · **Cột vật lý:** `PMT_CODE`

## Ý nghĩa nghiệp vụ

Cột PMT_CODE trên CASH_ST. db2:cash_st: CASH.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cash_st` | `PMT_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cash_st.PMT_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `CASH`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space)
