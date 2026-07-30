---
semantic_key: sale_document_number
title: Số chứng từ / bill — join header ↔ dòng ↔ thanh toán
display_names:
- TRANS_NUM
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: TRANS_NUM
  type: char
- ref: db1:pmtrans
  column: TRANS_NUM
  type: char
- ref: db1:strans
  column: TRANS_NUM
  type: char
- ref: db1:transhdr_arc
  column: TRANS_NUM
  type: char
- ref: db2:cash_st
  column: TRANS_NUM
  type: char
- ref: db2:crdtrans
  column: TRANS_NUM
  type: char
- ref: db2:crdtrans_tmp
  column: TRANS_NUM
  type: char
- ref: db2:ctrans
  column: TRANS_NUM
  type: char
- ref: db2:custhist
  column: TRANS_NUM
  type: char
- ref: db2:inv_iss
  column: TRANS_NUM
  type: char
- ref: db2:pmcrdiss
  column: TRANS_NUM
  type: char
- ref: db2:pmcrdrcv
  column: TRANS_NUM
  type: char
- ref: db2:pmcrdstk
  column: TRANS_NUM
  type: char
- ref: db2:pmtrans
  column: TRANS_NUM
  type: char
- ref: db2:st_order
  column: TRANS_NUM
  type: char
- ref: db2:strans
  column: TRANS_NUM
  type: char
- ref: db2:strans_tmp
  column: TRANS_NUM
  type: char
- ref: db2:suspend
  column: TRANS_NUM
  type: char
- ref: db2:transhdr
  column: TRANS_NUM
  type: char
join_with: []
related_semantic_keys: []
facts:
- Số chứng từ / bill; join header ↔ dòng ↔ thanh toán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số chứng từ / bill — join header ↔ dòng ↔ thanh toán

**Semantic key:** `sale_document_number` · **Cột vật lý:** `TRANS_NUM`

## Ý nghĩa nghiệp vụ

Số chứng từ / bill (TRANS_NUM) — khóa join TRANSHDR ↔ STRANS ↔ PMTRANS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db1:pmtrans` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db1:strans` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db1:transhdr_arc` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:cash_st` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:crdtrans` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:crdtrans_tmp` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:ctrans` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:custhist` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:inv_iss` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:pmcrdiss` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:pmcrdrcv` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:pmcrdstk` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:pmtrans` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:st_order` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:strans` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:strans_tmp` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:suspend` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| `db2:transhdr` | `TRANS_NUM` | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |

## Ghi chú thêm

- Số chứng từ / bill; join header ↔ dòng ↔ thanh toán.
- Companion / basket: các dòng khác trên cùng bill chia sẻ `TRANS_NUM` — lấy bằng
  `query_rows` với `trans_nums` từ dòng sản phẩm đã khớp (bỏ `sku_ids` ở bước expand).
  Join product-only lines × `TRANSHDR` không thêm SKU khác trên bill.
