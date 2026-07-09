---
semantic_key: amount_bill_header
title: Tổng tiền bill header — lọc min bill
display_names:
- AMOUNT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: AMOUNT
  type: numeric
- ref: db2:transhdr
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
- 'db1:transhdr_arc.AMOUNT: top=0.00(51), 14000.00(6), 18000.00(3), 1.00(3), 64000.00(2)'
- 'db2:transhdr.AMOUNT: top=0.00(31), 55077.78(3), 8264.47(3), 21254.00(3), 36750.00(3)'
---

# Tổng tiền bill header — lọc min bill

**Semantic key:** `amount_bill_header` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Tổng tiền bill trên TRANSHDR (TRANS_CODE=113). Dùng cho điều kiện min bill hợp lệ. Sample: 410000, 2206000, 732000 VND. Khác grain với AMOUNT dòng STRANS (line-level).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `AMOUNT` | numeric | có dữ liệu |
| `db2:transhdr` | `AMOUNT` | numeric | Tổng bill — dùng min bill |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `27315.46`×1, `53478.02`×1, `93650.82`×1, `88113.29`×1, `365745.74`×1, `15171.71`×1, `27508.17`×1, `56784.94`×1

### `db2:transhdr.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈15; top: `0.00`×6, `20000.00`×1, `751944.00`×1, `3525000.02`×1, `4550685.18`×1, `8050000.00`×1, `527370.00`×1, `401100.00`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)
