---
semantic_key: store_id_ref
title: store id ref
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
- Mã cửa hàng / kho (10001, 10004, 10005, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cash_st.STK_ID: top=10001(7)'
- 'db2:crdtrans_tmp.STK_ID: top=10001(617), 10004(229), 10005(153), 10002(1)'
- 'db2:ctrans.STK_ID: top=10001(456), 10004(278), 10005(219), 20002(40), 20001(7)'
- 'db2:custhist.STK_ID: top=10001(858), 10004(88), 10005(31), 20002(14), 20001(8)'
- 'db2:hissppr.STK_ID: top=10001(25)'
- 'db2:inv_iss.STK_ID: top=10001(703), 10004(225), 10005(72)'
- 'db2:pmcrdinf.STK_ID: top=10001(999)'
- 'db2:pmcrdiss.STK_ID: top=10001(1000)'
- 'db2:pmcrdrcv.STK_ID: top=10001(763), 10005(170), 10004(67)'
- 'db2:pmcrdstk.STK_ID: top=10001(1000)'
- 'db2:sku_activity.stk_id: top=10001(455), 10004(310), 10005(230), 20002(3), 20001(2)'
- 'db2:st_order.STK_ID: top=10001(838), 20001(92), 10004(68), 10005(2)'
- 'db2:stk_dtl.STK_ID: top=10001(802), 10004(155), 20001(32), 20002(5), 20003(3)'
- 'db2:strans_tmp.STK_ID: top=10001(624), 10004(216), 10005(160)'
- 'db2:suspend.STK_ID: top=10001(1000)'
- 'db2:webrpt_inventory_daily.stk_id: top=10001(537), 10004(231), 10005(227), 20001(3),
  20006(1)'
---

# store id ref

**Semantic key:** `store_id_ref` · **Cột vật lý:** `stk_id`, `STK_ID`

## Ý nghĩa nghiệp vụ

Cột STK_ID trên ACCOUNT, ASSOLST, CASH_ST. db2:cash_st: top 10001; db2:crdtrans_tmp: top 10001; db2:ctrans: top 10001, 10004, 10005; db2:custhist: top 10001; db2:inv_iss: top 10001; db2:pmcrdinf: top 10001; db2:pmcrdiss: top 10001; db2:pmcrdrcv: top 10001, 10005; db2:pmcrdstk: top 10001; db2:sku_activity: top 10001; db2:st_order: top 20001, 10001; db2:stk_dtl: top 10001; db2:strans_tmp: top 10001, 20002, 10005; db2:suspend: top 10001; db2:webrpt_inventory_daily: top 10001.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:assolst` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:cash_st` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:crdtrans_tmp` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:ctrans` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:custhist` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:customer` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:hissppr` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:inv_hdr` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:inv_iss` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:partner` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:pmcrdinf` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:pmcrdiss` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:pmcrdrcv` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:pmcrdstk` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:sku_activity` | `stk_id` | varchar | Cửa hàng — sample 10001 |
| `db2:st_order` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:stk_dtl` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:strans_tmp` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:supplier` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:suspend` | `STK_ID` | char | Cửa hàng — sample 10001 |
| `db2:webrpt_inventory_daily` | `stk_id` | varchar | Cửa hàng — sample 10001 |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cash_st.STK_ID`
- Null rate trong sample: 45%
- Distinct ≈1; top: `10001`×11

### `db2:crdtrans_tmp.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:ctrans.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈3; top: `10001`×11, `10004`×6, `10005`×3

### `db2:custhist.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:inv_iss.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:pmcrdinf.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:pmcrdiss.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:pmcrdrcv.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `10001`×15, `10005`×5

### `db2:pmcrdstk.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:sku_activity.stk_id`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:st_order.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `20001`×17, `10001`×3

### `db2:stk_dtl.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:strans_tmp.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈4; top: `10001`×8, `20002`×7, `10005`×3, `10004`×2

### `db2:suspend.STK_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

### `db2:webrpt_inventory_daily.stk_id`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

## Ghi chú thêm

- Mã cửa hàng / kho (10001, 10004, 10005, …)
