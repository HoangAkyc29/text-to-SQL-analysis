---
semantic_key: trans_code
title: Loại chứng từ (TRANS_CODE)
display_names:
- TRANS_CODE
kind: code
tables:
- ref: db2:cash_st
  column: TRANS_CODE
  type: char
- ref: db2:ctrans
  column: TRANS_CODE
  type: char
- ref: db2:custhist
  column: TRANS_CODE
  type: char
- ref: db2:inv_iss
  column: TRANS_CODE
  type: char
- ref: db2:pmcrdiss
  column: TRANS_CODE
  type: char
- ref: db2:pmcrdrcv
  column: TRANS_CODE
  type: char
- ref: db2:pmcrdstk
  column: TRANS_CODE
  type: char
- ref: db2:st_order
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
- column_semantic_registry
- business_prose
---

# Loại chứng từ (TRANS_CODE)

**Semantic key:** `trans_code` · **Cột vật lý:** `TRANS_CODE`

## Ý nghĩa nghiệp vụ

Phân loại loại chứng từ trong hệ POS/ERP. 113 = bán lẻ; 221 = thanh toán bill; 811/812 = tích điểm / điều chỉnh loyalty — grain phụ thuộc bảng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cash_st` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:ctrans` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:custhist` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:inv_iss` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:pmcrdiss` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:pmcrdrcv` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:pmcrdstk` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| `db2:st_order` | `TRANS_CODE` | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)
