---
semantic_key: status
title: status
display_names:
- STATUS
kind: flag
tables:
- ref: db1:crdtrans_arc
  column: STATUS
  type: bit
- ref: db1:pmtrans
  column: STATUS
  type: bit
- ref: db1:strans
  column: STATUS
  type: char
- ref: db1:transhdr_arc
  column: STATUS
  type: char
- ref: db2:account
  column: STATUS
  type: bit
- ref: db2:asso_inf
  column: STATUS
  type: bit
- ref: db2:assolst
  column: STATUS
  type: bit
- ref: db2:cash_st
  column: STATUS
  type: bit
- ref: db2:crdtrans
  column: STATUS
  type: bit
- ref: db2:crdtrans_tmp
  column: STATUS
  type: bit
- ref: db2:cscard
  column: STATUS
  type: bit
- ref: db2:ctrans
  column: STATUS
  type: bit
- ref: db2:customer
  column: STATUS
  type: bit
- ref: db2:debt
  column: STATUS
  type: bit
- ref: db2:inv_hdr
  column: STATUS
  type: bit
- ref: db2:inv_iss
  column: STATUS
  type: bit
- ref: db2:partner
  column: STATUS
  type: bit
- ref: db2:plu
  column: STATUS
  type: bit
- ref: db2:pmcrdinf
  column: STATUS
  type: bit
- ref: db2:pmcrdiss
  column: STATUS
  type: bit
- ref: db2:pmcrdrcv
  column: STATUS
  type: char
- ref: db2:pmcrdstk
  column: STATUS
  type: bit
- ref: db2:pmtrans
  column: STATUS
  type: bit
- ref: db2:rdiscinf
  column: STATUS
  type: bit
- ref: db2:sku_def
  column: STATUS
  type: char
- ref: db2:st_order
  column: STATUS
  type: char
- ref: db2:strans
  column: STATUS
  type: char
- ref: db2:strans_tmp
  column: STATUS
  type: char
- ref: db2:supplier
  column: STATUS
  type: bit
- ref: db2:suspend
  column: STATUS
  type: bit
- ref: db2:transhdr
  column: STATUS
  type: char
join_with: []
related_semantic_keys: []
facts:
- Trạng thái active/duyệt
sources:
- table_md
- column_semantic_registry
- business_prose
---

# status

**Semantic key:** `status` · **Cột vật lý:** `STATUS`

## Ý nghĩa nghiệp vụ

Trạng thái bản ghi / chứng từ (active, closed, cancelled, …) — ý nghĩa cụ thể theo bảng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `STATUS` | bit | Trạng thái active/duyệt |
| `db1:pmtrans` | `STATUS` | bit | Trạng thái active/duyệt |
| `db1:strans` | `STATUS` | char | Trạng thái active/duyệt |
| `db1:transhdr_arc` | `STATUS` | char | Trạng thái active/duyệt |
| `db2:account` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:asso_inf` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:assolst` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:cash_st` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:crdtrans` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:crdtrans_tmp` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:cscard` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:ctrans` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:customer` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:debt` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:inv_hdr` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:inv_iss` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:partner` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:plu` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:pmcrdinf` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:pmcrdiss` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:pmcrdrcv` | `STATUS` | char | Trạng thái active/duyệt |
| `db2:pmcrdstk` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:pmtrans` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:rdiscinf` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:sku_def` | `STATUS` | char | Trạng thái active/duyệt |
| `db2:st_order` | `STATUS` | char | Trạng thái active/duyệt |
| `db2:strans` | `STATUS` | char | Trạng thái active/duyệt |
| `db2:strans_tmp` | `STATUS` | char | Trạng thái active/duyệt |
| `db2:supplier` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:suspend` | `STATUS` | bit | Trạng thái active/duyệt |
| `db2:transhdr` | `STATUS` | char | Trạng thái active/duyệt |

## Ghi chú thêm

- Trạng thái active/duyệt
