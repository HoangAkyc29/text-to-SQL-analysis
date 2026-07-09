---
semantic_key: amount
title: amount
display_names:
- Amount
- AMOUNT
kind: measure
tables:
- ref: db2:custhist
  column: AMOUNT
  type: numeric
- ref: db2:custsumm
  column: Amount
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
- 'db2:custhist.AMOUNT: top=500000.00(9), 260000.00(7), 300000.00(7), 200000.00(6),
  675000.00(6)'
- 'db2:custsumm.Amount: top=153500(2), 540750(2), 1532708(1), 405176(1), 1806000(1)'
---

# amount

**Semantic key:** `amount` · **Cột vật lý:** `Amount`, `AMOUNT`

## Ý nghĩa nghiệp vụ

Cột AMOUNT trên CUSTHIST, CUSTSUMM. db2:custhist: top 1732800.00, 290700.00, 581400.00; db2:custsumm: top 1741444, 592668, 1794431.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:custhist` | `AMOUNT` | numeric | có dữ liệu |
| `db2:custsumm` | `Amount` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:custhist.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈14; top: `1732800.00`×4, `290700.00`×3, `581400.00`×2, `1243620.00`×1, `414540.00`×1, `24225.00`×1, `1550400.00`×1, `3683625.00`×1

### `db2:custsumm.Amount`
- Null rate trong sample: 0%
- Distinct ≈20; top: `1741444`×1, `592668`×1, `1794431`×1, `6952989`×1, `933100`×1, `13831732`×1, `268500`×1, `674300`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
