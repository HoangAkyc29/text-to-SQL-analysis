---
semantic_key: store_id_ref
title: Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)
display_names:
- stk_id
- STK_ID
kind: identifier
tables:
- ref: db2:account
  column: STK_ID
  type: char
- ref: db2:assolst
  column: STK_ID
  type: char
- ref: db2:cash_st
  column: STK_ID
  type: char
- ref: db2:crdtrans_tmp
  column: STK_ID
  type: char
- ref: db2:ctrans
  column: STK_ID
  type: char
- ref: db2:custhist
  column: STK_ID
  type: char
- ref: db2:customer
  column: STK_ID
  type: char
- ref: db2:hissppr
  column: STK_ID
  type: char
- ref: db2:inv_hdr
  column: STK_ID
  type: char
- ref: db2:inv_iss
  column: STK_ID
  type: char
- ref: db2:partner
  column: STK_ID
  type: char
- ref: db2:pmcrdinf
  column: STK_ID
  type: char
- ref: db2:pmcrdiss
  column: STK_ID
  type: char
- ref: db2:pmcrdrcv
  column: STK_ID
  type: char
- ref: db2:pmcrdstk
  column: STK_ID
  type: char
- ref: db2:sku_activity
  column: stk_id
  type: varchar
- ref: db2:st_order
  column: STK_ID
  type: char
- ref: db2:stk_dtl
  column: STK_ID
  type: char
- ref: db2:strans_tmp
  column: STK_ID
  type: char
- ref: db2:supplier
  column: STK_ID
  type: char
- ref: db2:suspend
  column: STK_ID
  type: char
- ref: db2:webrpt_inventory_daily
  column: stk_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã cửa hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã cửa hàng / siêu thị phát sinh giao dịch (STK_ID)

**Semantic key:** `store_id_ref` · **Cột vật lý:** `stk_id`, `STK_ID`

## Ý nghĩa nghiệp vụ

Mã cửa hàng trên báo cáo — grain store × SKU × ngày. (bảng WEBRPT_INVENTORY_DAILY).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:assolst` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:cash_st` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:crdtrans_tmp` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:ctrans` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:custhist` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:customer` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:hissppr` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:inv_hdr` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:inv_iss` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:partner` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:pmcrdinf` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:pmcrdiss` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:pmcrdrcv` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:pmcrdstk` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:sku_activity` | `stk_id` | varchar | Mã cửa hàng |
| `db2:st_order` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:stk_dtl` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:strans_tmp` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:supplier` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:suspend` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:webrpt_inventory_daily` | `stk_id` | varchar | Mã cửa hàng |
