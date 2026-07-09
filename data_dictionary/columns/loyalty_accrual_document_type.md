---
semantic_key: loyalty_accrual_document_type
title: Loại GD tích điểm live — 811 (CRDTRANS db2)
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db2:crdtrans
  column: TRANS_CODE
  type: char
- ref: db2:crdtrans_tmp
  column: TRANS_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ,
  008=quỹ, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crdtrans.TRANS_CODE: top=221(984), 812(9), 811(6), 222(1)'
- 'db2:crdtrans_tmp.TRANS_CODE: top=221(1000)'
---

# Loại GD tích điểm live — 811 (CRDTRANS db2)

**Semantic key:** `loyalty_accrual_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

TRANS_CODE=811 trên CRDTRANS (db2 live) — giao dịch tích điểm từ mua hàng/thanh toán.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crdtrans` | `TRANS_CODE` | char | 811 = tích điểm live |
| `db2:crdtrans_tmp` | `TRANS_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crdtrans.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `811`×20

### `db2:crdtrans_tmp.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `221`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
