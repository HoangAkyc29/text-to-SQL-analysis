---
semantic_key: amount_invoice_issue
title: amount invoice issue
display_names:
- AMOUNT
kind: measure
tables:
- ref: db2:inv_iss
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
- 'db2:inv_iss.AMOUNT: top=19904.76(8), 11428.57(7), 1.00(5), 9523.81(5), 15714.29(4)'
---

# amount invoice issue

**Semantic key:** `amount_invoice_issue` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Thành tiền / số tiền (ngữ cảnh theo bảng)

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `AMOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_iss.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `13804439.70`×1, `4426824.42`×1, `235648.15`×1, `459653.20`×1, `105733.34`×1, `235185.19`×1, `296426.15`×1, `32331.43`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

