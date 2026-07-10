---
semantic_key: ws_id
title: Mã máy trạm (workstation) (WS_ID)
display_names:
- WS_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: WS_ID
  type: int
- ref: db1:pmtrans
  column: WS_ID
  type: int
- ref: db1:strans
  column: WS_ID
  type: int
- ref: db1:transhdr_arc
  column: WS_ID
  type: int
- ref: db2:assolst
  column: WS_ID
  type: int
- ref: db2:cash_st
  column: WS_ID
  type: int
- ref: db2:crdtrans
  column: WS_ID
  type: int
- ref: db2:crdtrans_tmp
  column: WS_ID
  type: int
- ref: db2:ctrans
  column: WS_ID
  type: int
- ref: db2:hisrtpr
  column: WS_ID
  type: int
- ref: db2:hissppr
  column: WS_ID
  type: int
- ref: db2:inv_iss
  column: WS_ID
  type: int
- ref: db2:plu
  column: WS_ID
  type: int
- ref: db2:pmcrdiss
  column: WS_ID
  type: int
- ref: db2:pmcrdstk
  column: WS_ID
  type: int
- ref: db2:pmtrans
  column: WS_ID
  type: int
- ref: db2:sku_def
  column: WS_ID
  type: int
- ref: db2:st_order
  column: WS_ID
  type: int
- ref: db2:strans
  column: WS_ID
  type: int
- ref: db2:strans_tmp
  column: WS_ID
  type: int
- ref: db2:suspend
  column: WS_ID
  type: int
- ref: db2:transhdr
  column: WS_ID
  type: int
join_with: []
related_semantic_keys: []
facts:
- Mã máy trạm
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã máy trạm (workstation) (WS_ID)

**Semantic key:** `ws_id` · **Cột vật lý:** `WS_ID`

## Ý nghĩa nghiệp vụ

Mã máy trạm. Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …); Kho / mua hàng (INV_ISS, ST_ORDER); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `WS_ID` | int | Mã máy trạm |
| `db1:pmtrans` | `WS_ID` | int | Mã máy trạm |
| `db1:strans` | `WS_ID` | int | Mã máy trạm |
| `db1:transhdr_arc` | `WS_ID` | int | Mã máy trạm |
| `db2:assolst` | `WS_ID` | int | Mã máy trạm |
| `db2:cash_st` | `WS_ID` | int | Mã máy trạm |
| `db2:crdtrans` | `WS_ID` | int | Mã máy trạm |
| `db2:crdtrans_tmp` | `WS_ID` | int | Mã máy trạm |
| `db2:ctrans` | `WS_ID` | int | Mã máy trạm |
| `db2:hisrtpr` | `WS_ID` | int | Mã máy trạm |
| `db2:hissppr` | `WS_ID` | int | Mã máy trạm |
| `db2:inv_iss` | `WS_ID` | int | Mã máy trạm |
| `db2:plu` | `WS_ID` | int | Mã máy trạm |
| `db2:pmcrdiss` | `WS_ID` | int | Mã máy trạm |
| `db2:pmcrdstk` | `WS_ID` | int | Mã máy trạm |
| `db2:pmtrans` | `WS_ID` | int | Mã máy trạm |
| `db2:sku_def` | `WS_ID` | int | Mã máy trạm |
| `db2:st_order` | `WS_ID` | int | Mã máy trạm |
| `db2:strans` | `WS_ID` | int | Mã máy trạm |
| `db2:strans_tmp` | `WS_ID` | int | Mã máy trạm |
| `db2:suspend` | `WS_ID` | int | Mã máy trạm |
| `db2:transhdr` | `WS_ID` | int | Mã máy trạm |
