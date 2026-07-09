---
semantic_key: payment_document_type
title: Loại chứng từ thanh toán — 221/222/008
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db1:pmtrans
  column: TRANS_CODE
  type: char
- ref: db2:pmtrans
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
- 'db1:pmtrans.TRANS_CODE: top=221(989), 008(6), 222(5)'
- 'db2:pmtrans.TRANS_CODE: top=221(984), 008(8), 010(6), 222(2)'
---

# Loại chứng từ thanh toán — 221/222/008

**Semantic key:** `payment_document_type` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Loại chứng từ TRANS_CODE — thanh toán 221 / quỹ 008. db1:pmtrans: mã 221=thanh toán bill; db2:pmtrans: mã 222=thanh toán/điều chỉnh khác, 008=thu/chi quỹ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `TRANS_CODE` | char | 221/222/008 thanh toán hoặc quỹ |
| `db2:pmtrans` | `TRANS_CODE` | char | 221/222/008 thanh toán hoặc quỹ |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `221`×20

### `db2:pmtrans.TRANS_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `222`×17, `008`×3

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
