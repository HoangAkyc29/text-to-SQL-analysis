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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.STATUS: top=True(698), False(302)'
- 'db1:pmtrans.STATUS: top=True(1000)'
- 'db1:strans.STATUS: top=N(872), R(108), M(20)'
- 'db1:transhdr_arc.STATUS: top=N(936), R(58), M(5), D(1)'
- 'db2:account.STATUS: top=True(1000)'
- 'db2:asso_inf.STATUS: top=True(1000)'
- 'db2:assolst.STATUS: top=True(1000)'
- 'db2:cash_st.STATUS: top=True(998), False(2)'
- 'db2:crdtrans.STATUS: top=True(999), False(1)'
- 'db2:crdtrans_tmp.STATUS: top=True(1000)'
- 'db2:cscard.STATUS: top=True(912), False(88)'
- 'db2:ctrans.STATUS: top=True(1000)'
- 'db2:customer.STATUS: top=True(1000)'
- 'db2:debt.STATUS: top=True(1000)'
- 'db2:inv_hdr.STATUS: top=True(998), False(2)'
- 'db2:inv_iss.STATUS: top=True(1000)'
- 'db2:partner.STATUS: top=True(999), False(1)'
- 'db2:plu.STATUS: top=True(1000)'
- 'db2:pmcrdinf.STATUS: top=False(717), True(283)'
- 'db2:pmcrdiss.STATUS: top=True(1000)'
- 'db2:pmcrdrcv.STATUS: top=N(757), R(243)'
- 'db2:pmcrdstk.STATUS: top=True(1000)'
- 'db2:pmtrans.STATUS: top=True(999), False(1)'
- 'db2:rdiscinf.STATUS: top=True(972), False(28)'
- 'db2:sku_def.STATUS: top=01(1000)'
- 'db2:st_order.STATUS: top=E(1000)'
- 'db2:strans.STATUS: top=N(867), R(117), M(15), D(1)'
- 'db2:strans_tmp.STATUS: top=N(913), R(86), D(1)'
- 'db2:supplier.STATUS: top=True(999), False(1)'
- 'db2:suspend.STATUS: top=False(1000)'
- 'db2:transhdr.STATUS: top=N(914), R(84), M(2)'
---

# status

**Semantic key:** `status` · **Cột vật lý:** `STATUS`

## Ý nghĩa nghiệp vụ

Cột STATUS trên ACCOUNT, ASSOLST, ASSO_INF. db1:crdtrans_arc: top True; db1:pmtrans: top True; db1:strans: top N; db1:transhdr_arc: top N, R; db2:account: top True; db2:asso_inf: top True; db2:assolst: top True; db2:cash_st: top True; db2:crdtrans: top True; db2:crdtrans_tmp: top True; db2:cscard: top False, True; db2:ctrans: top True; db2:customer: top True; db2:debt: top True; db2:inv_hdr: top True; db2:inv_iss: top True; db2:partner: top True; db2:plu: top True; db2:pmcrdinf: top True; db2:pmcrdiss: top True; db2:pmcrdrcv: top N, R; db2:pmcrdstk: top True; db2:pmtrans: top True; db2:rdiscinf: top True, False; db2:sku_def: top 01; db2:st_order: top E; db2:strans: top N; db2:strans_tmp: top N; db2:supplier: top True; db2:suspend: top False; db2:transhdr: top N, M.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `STATUS` | bit | có dữ liệu |
| `db1:pmtrans` | `STATUS` | bit | có dữ liệu |
| `db1:strans` | `STATUS` | char | có dữ liệu |
| `db1:transhdr_arc` | `STATUS` | char | có dữ liệu |
| `db2:account` | `STATUS` | bit | có dữ liệu |
| `db2:asso_inf` | `STATUS` | bit | có dữ liệu |
| `db2:assolst` | `STATUS` | bit | có dữ liệu |
| `db2:cash_st` | `STATUS` | bit | có dữ liệu |
| `db2:crdtrans` | `STATUS` | bit | có dữ liệu |
| `db2:crdtrans_tmp` | `STATUS` | bit | có dữ liệu |
| `db2:cscard` | `STATUS` | bit | có dữ liệu |
| `db2:ctrans` | `STATUS` | bit | có dữ liệu |
| `db2:customer` | `STATUS` | bit | có dữ liệu |
| `db2:debt` | `STATUS` | bit | có dữ liệu |
| `db2:inv_hdr` | `STATUS` | bit | có dữ liệu |
| `db2:inv_iss` | `STATUS` | bit | có dữ liệu |
| `db2:partner` | `STATUS` | bit | có dữ liệu |
| `db2:plu` | `STATUS` | bit | có dữ liệu |
| `db2:pmcrdinf` | `STATUS` | bit | có dữ liệu |
| `db2:pmcrdiss` | `STATUS` | bit | có dữ liệu |
| `db2:pmcrdrcv` | `STATUS` | char | có dữ liệu |
| `db2:pmcrdstk` | `STATUS` | bit | có dữ liệu |
| `db2:pmtrans` | `STATUS` | bit | có dữ liệu |
| `db2:rdiscinf` | `STATUS` | bit | có dữ liệu |
| `db2:sku_def` | `STATUS` | char | có dữ liệu |
| `db2:st_order` | `STATUS` | char | có dữ liệu |
| `db2:strans` | `STATUS` | char | có dữ liệu |
| `db2:strans_tmp` | `STATUS` | char | có dữ liệu |
| `db2:supplier` | `STATUS` | bit | có dữ liệu |
| `db2:suspend` | `STATUS` | bit | có dữ liệu |
| `db2:transhdr` | `STATUS` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db1:pmtrans.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db1:strans.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `N`×20

### `db1:transhdr_arc.STATUS`
- Null rate trong sample: 0%
- Distinct ≈2; top: `N`×19, `R`×1

### `db2:account.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:asso_inf.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:assolst.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:cash_st.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:crdtrans.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:crdtrans_tmp.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:cscard.STATUS`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×16, `True`×4

### `db2:ctrans.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:customer.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:debt.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:inv_hdr.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:inv_iss.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:partner.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:plu.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:pmcrdinf.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:pmcrdiss.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:pmcrdrcv.STATUS`
- Null rate trong sample: 0%
- Distinct ≈2; top: `N`×10, `R`×10

### `db2:pmcrdstk.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:pmtrans.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:rdiscinf.STATUS`
- Null rate trong sample: 0%
- Distinct ≈2; top: `True`×15, `False`×5

### `db2:sku_def.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:st_order.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `E`×20

### `db2:strans.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `N`×20

### `db2:strans_tmp.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `N`×20

### `db2:supplier.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:suspend.STATUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:transhdr.STATUS`
- Null rate trong sample: 0%
- Distinct ≈2; top: `N`×15, `M`×5

## Ghi chú thêm

- Trạng thái active/duyệt
