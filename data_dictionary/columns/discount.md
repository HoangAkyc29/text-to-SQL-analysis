---
semantic_key: discount
title: Giảm giá / chiết khấu (DISCOUNT)
display_names:
- DISCOUNT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: DISCOUNT
  type: numeric
- ref: db1:strans
  column: DISCOUNT
  type: numeric
- ref: db1:transhdr_arc
  column: DISCOUNT
  type: numeric
- ref: db2:crdtrans
  column: DISCOUNT
  type: numeric
- ref: db2:crdtrans_tmp
  column: DISCOUNT
  type: numeric
- ref: db2:inv_hdr
  column: DISCOUNT
  type: numeric
- ref: db2:inv_iss
  column: DISCOUNT
  type: numeric
- ref: db2:partner
  column: DISCOUNT
  type: numeric
- ref: db2:st_order
  column: DISCOUNT
  type: decimal
- ref: db2:strans
  column: DISCOUNT
  type: numeric
- ref: db2:strans_tmp
  column: DISCOUNT
  type: numeric
- ref: db2:suspend
  column: DISCOUNT
  type: numeric
- ref: db2:transhdr
  column: DISCOUNT
  type: numeric
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Giảm giá (số tiền hoặc % tùy ngữ cảnh)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giảm giá / chiết khấu (DISCOUNT)

**Semantic key:** `discount` · **Cột vật lý:** `DISCOUNT`

## Ý nghĩa nghiệp vụ

Giảm giá / chiết khấu trên chứng từ bán. STRANS: chiết khấu từng dòng; TRANSHDR: tổng giảm trên bill. Có thể bằng 0 với hàng không KM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db1:strans` | `DISCOUNT` | numeric | giảm giá / chiết khấu trên dòng bán |
| `db1:transhdr_arc` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:crdtrans` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:crdtrans_tmp` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:inv_hdr` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:inv_iss` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:partner` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:st_order` | `DISCOUNT` | decimal | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:strans` | `DISCOUNT` | numeric | giảm giá / chiết khấu trên dòng bán |
| `db2:strans_tmp` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:suspend` | `DISCOUNT` | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| `db2:transhdr` | `DISCOUNT` | numeric | tổng giảm giá trên header bill |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Giảm giá (số tiền hoặc % tùy ngữ cảnh)
