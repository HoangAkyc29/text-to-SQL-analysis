---
semantic_key: amount_debt_entry
title: amount debt entry
display_names:
- AMOUNT
kind: measure
tables:
- ref: db2:ctrans
  column: AMOUNT
  type: numeric
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Thành tiền / số tiền (ngữ cảnh theo bảng)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for AMOUNT
- 'db2:ctrans.AMOUNT: top=430000.00(4), 590000.00(3), 1290000.00(3), 705000.00(3),
  1390000.05(3)'
---

# amount debt entry

**Semantic key:** `amount_debt_entry` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Thành tiền / số tiền (ngữ cảnh theo bảng)

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `AMOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `20000.00`×1, `751944.00`×1, `3525000.02`×1, `4550685.18`×1, `8050000.00`×1, `527370.00`×1, `401100.00`×1, `705000.00`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

