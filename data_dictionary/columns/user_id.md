---
semantic_key: user_id
title: Mã user thao tác (USER_ID)
display_names:
- USER_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: USER_ID
  type: int
- ref: db1:pmtrans
  column: USER_ID
  type: int
- ref: db1:strans
  column: USER_ID
  type: int
- ref: db1:transhdr_arc
  column: USER_ID
  type: int
- ref: db2:assolst
  column: USER_ID
  type: int
- ref: db2:cash_st
  column: USER_ID
  type: int
- ref: db2:crdtrans
  column: USER_ID
  type: int
- ref: db2:crdtrans_tmp
  column: USER_ID
  type: int
- ref: db2:ctrans
  column: USER_ID
  type: int
- ref: db2:hisrtpr
  column: USER_ID
  type: int
- ref: db2:hissppr
  column: USER_ID
  type: int
- ref: db2:inv_iss
  column: USER_ID
  type: int
- ref: db2:plu
  column: USER_ID
  type: int
- ref: db2:pmcrdiss
  column: USER_ID
  type: int
- ref: db2:pmcrdstk
  column: USER_ID
  type: int
- ref: db2:pmtrans
  column: USER_ID
  type: int
- ref: db2:sku_def
  column: USER_ID
  type: int
- ref: db2:st_order
  column: USER_ID
  type: int
- ref: db2:strans
  column: USER_ID
  type: int
- ref: db2:strans_tmp
  column: USER_ID
  type: int
- ref: db2:suspend
  column: USER_ID
  type: int
- ref: db2:transhdr
  column: USER_ID
  type: int
join_with: []
related_semantic_keys: []
facts:
- Mã user thao tác
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã user thao tác (USER_ID)

**Semantic key:** `user_id` · **Cột vật lý:** `USER_ID`

## Ý nghĩa nghiệp vụ

Mã user thao tác. Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …); Kho / mua hàng (INV_ISS, ST_ORDER); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `USER_ID` | int | Mã user thao tác |
| `db1:pmtrans` | `USER_ID` | int | Mã user thao tác |
| `db1:strans` | `USER_ID` | int | Mã user thao tác |
| `db1:transhdr_arc` | `USER_ID` | int | Mã user thao tác |
| `db2:assolst` | `USER_ID` | int | Mã user thao tác |
| `db2:cash_st` | `USER_ID` | int | Mã user thao tác |
| `db2:crdtrans` | `USER_ID` | int | Mã user thao tác |
| `db2:crdtrans_tmp` | `USER_ID` | int | Mã user thao tác |
| `db2:ctrans` | `USER_ID` | int | Mã user thao tác |
| `db2:hisrtpr` | `USER_ID` | int | Mã user thao tác |
| `db2:hissppr` | `USER_ID` | int | Mã user thao tác |
| `db2:inv_iss` | `USER_ID` | int | Mã user thao tác |
| `db2:plu` | `USER_ID` | int | Mã user thao tác |
| `db2:pmcrdiss` | `USER_ID` | int | Mã user thao tác |
| `db2:pmcrdstk` | `USER_ID` | int | Mã user thao tác |
| `db2:pmtrans` | `USER_ID` | int | Mã user thao tác |
| `db2:sku_def` | `USER_ID` | int | Mã user thao tác |
| `db2:st_order` | `USER_ID` | int | Mã user thao tác |
| `db2:strans` | `USER_ID` | int | Mã user thao tác |
| `db2:strans_tmp` | `USER_ID` | int | Mã user thao tác |
| `db2:suspend` | `USER_ID` | int | Mã user thao tác |
| `db2:transhdr` | `USER_ID` | int | Mã user thao tác |
