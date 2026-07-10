---
semantic_key: bu_id
title: Mã đơn vị kinh doanh / chi nhánh logic (BU_ID)
display_names:
- BU_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: BU_ID
  type: char
- ref: db1:pmtrans
  column: BU_ID
  type: char
- ref: db1:strans
  column: BU_ID
  type: char
- ref: db1:transhdr_arc
  column: BU_ID
  type: char
- ref: db2:cash_st
  column: BU_ID
  type: char
- ref: db2:crdtrans
  column: BU_ID
  type: char
- ref: db2:crdtrans_tmp
  column: BU_ID
  type: char
- ref: db2:cscard
  column: BU_ID
  type: char
- ref: db2:ctrans
  column: BU_ID
  type: char
- ref: db2:customer
  column: BU_ID
  type: char
- ref: db2:inv_iss
  column: BU_ID
  type: char
- ref: db2:pmcrdiss
  column: BU_ID
  type: char
- ref: db2:pmcrdrcv
  column: BU_ID
  type: char
- ref: db2:pmcrdstk
  column: BU_ID
  type: char
- ref: db2:pmtrans
  column: BU_ID
  type: char
- ref: db2:st_order
  column: BU_ID
  type: char
- ref: db2:strans
  column: BU_ID
  type: char
- ref: db2:strans_tmp
  column: BU_ID
  type: char
- ref: db2:suspend
  column: BU_ID
  type: char
- ref: db2:transhdr
  column: BU_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã đơn vị kinh doanh / chi nhánh logic (BU_ID)

**Semantic key:** `bu_id` · **Cột vật lý:** `BU_ID`

## Ý nghĩa nghiệp vụ

Mã đơn vị kinh doanh / chi nhánh logic trong tập đoàn — phân tách dữ liệu theo BU trên quỹ, kho, POS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db1:pmtrans` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db1:strans` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db1:transhdr_arc` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:cash_st` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:crdtrans` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:crdtrans_tmp` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:cscard` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:ctrans` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:customer` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:inv_iss` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:pmcrdiss` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:pmcrdrcv` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:pmcrdstk` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:pmtrans` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:st_order` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:strans` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:strans_tmp` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:suspend` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| `db2:transhdr` | `BU_ID` | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |

## Ghi chú thêm

- Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200)
