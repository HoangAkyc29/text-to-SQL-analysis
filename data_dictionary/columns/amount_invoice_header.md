---
semantic_key: amount_invoice_header
title: amount invoice header
display_names:
- AMOUNT
kind: measure
tables:
- ref: db2:inv_hdr
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
- 'db2:inv_hdr.AMOUNT: top=630000.00(6), 420000.00(4), 840000.00(4), 1039848.00(3),
  1968000.00(2)'
---

# amount invoice header

**Semantic key:** `amount_invoice_header` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Thành tiền / số tiền (ngữ cảnh theo bảng)

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_hdr` | `AMOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_hdr.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `4784880.20`×1, `630000.00`×1, `2333333.52`×1, `1791000.00`×1, `2878100.00`×1, `460100.00`×1, `22767977.67`×1, `2829626.40`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

