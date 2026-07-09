---
semantic_key: vat_amt
title: vat amt
display_names:
- VAT_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: VAT_AMT
  type: numeric
- ref: db1:strans
  column: VAT_AMT
  type: numeric
- ref: db1:transhdr_arc
  column: VAT_AMT
  type: numeric
- ref: db2:crdtrans
  column: VAT_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: VAT_AMT
  type: numeric
- ref: db2:custhist
  column: VAT_AMT
  type: numeric
- ref: db2:inv_hdr
  column: VAT_AMT
  type: numeric
- ref: db2:inv_iss
  column: VAT_AMT
  type: numeric
- ref: db2:st_order
  column: VAT_AMT
  type: decimal
- ref: db2:strans
  column: VAT_AMT
  type: numeric
- ref: db2:strans_tmp
  column: VAT_AMT
  type: numeric
- ref: db2:suspend
  column: VAT_AMT
  type: numeric
- ref: db2:transhdr
  column: VAT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tiền thuế VAT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.VAT_AMT: top=0.00(1000)'
- 'db1:strans.VAT_AMT: top=0.00(387), 2437.04(6), 851.85(6), 2111.11(6), 666.67(5)'
- 'db1:transhdr_arc.VAT_AMT: top=0.00(125), 4370.37(3), 2592.59(3), 1481.48(3), 2362.96(3)'
- 'db2:crdtrans.VAT_AMT: top=0.00(1000)'
- 'db2:crdtrans_tmp.VAT_AMT: top=0.00(1000)'
- 'db2:custhist.VAT_AMT: top=0.00(607), 42000.00(3), 64000.00(2), 216000.00(2), 35555.56(2)'
- 'db2:inv_hdr.VAT_AMT: top=0.00(15), 50400.00(5), 67200.00(4), 33600.00(3), 83187.84(3)'
- 'db2:inv_iss.VAT_AMT: top=0.00(10), 995.24(8), 571.43(7), 476.19(5), 785.71(4)'
- 'db2:st_order.VAT_AMT: top=0.00(1000)'
- 'db2:strans.VAT_AMT: top=0.00(177), 74.07(31), 59.26(23), 88.89(15), 37.04(13)'
- 'db2:strans_tmp.VAT_AMT: top=0.00(271), 1481.48(15), 1000.00(8), 1851.85(7), 696.30(6)'
- 'db2:suspend.VAT_AMT: top=0.00(1000)'
- 'db2:transhdr.VAT_AMT: top=0.00(43), 74.07(5), 3185.19(5), 4740.74(5), 2148.15(4)'
---

# vat amt

**Semantic key:** `vat_amt` · **Cột vật lý:** `VAT_AMT`

## Ý nghĩa nghiệp vụ

Cột VAT_AMT trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db1:strans: top 28518.52, 0.00, 4680.00; db1:transhdr_arc: top 2792.59, 1963.81, 10303.70; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00; db2:custhist: top 0.00, 29070.00, 58140.00; db2:inv_hdr: top 382790.42, 31500.00, 116666.68; db2:inv_iss: top 1022489.30, 328836.58, 18851.85; db2:st_order: top 0.00; db2:strans: top 1000.00, 9360.00, 10920.00; db2:strans_tmp: top 1132000.00, 353333.33, 747703.70; db2:suspend: top 0.00; db2:transhdr: top 0.00, 10192.00, 1000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `VAT_AMT` | numeric | có dữ liệu |
| `db1:strans` | `VAT_AMT` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:crdtrans` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:custhist` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:inv_hdr` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:inv_iss` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `VAT_AMT` | decimal | có dữ liệu |
| `db2:strans` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `VAT_AMT` | numeric | có dữ liệu |
| `db2:transhdr` | `VAT_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db1:strans.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈19; top: `28518.52`×2, `0.00`×1, `4680.00`×1, `63360.00`×1, `13500.00`×1, `49074.00`×1, `80000.00`×1, `50000.00`×1

### `db1:transhdr_arc.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `2792.59`×1, `1963.81`×1, `10303.70`×1, `8377.78`×1, `11057.68`×1, `1644.44`×1, `2644.44`×1, `4405.49`×1

### `db2:crdtrans.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:custhist.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈8; top: `0.00`×10, `29070.00`×3, `58140.00`×2, `124362.00`×1, `41454.00`×1, `2422.50`×1, `108300.00`×1, `54150.00`×1

### `db2:inv_hdr.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `382790.42`×1, `31500.00`×1, `116666.68`×1, `89550.00`×1, `143905.00`×1, `9880.00`×1, `1821438.23`×1, `226370.11`×1

### `db2:inv_iss.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `1022489.30`×1, `328836.58`×1, `18851.85`×1, `44946.80`×1, `5286.66`×1, `18814.81`×1, `19776.85`×1, `1616.57`×1

### `db2:st_order.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `1000.00`×1, `9360.00`×1, `10920.00`×1, `16320.00`×1, `23555.52`×1, `57037.04`×1, `63703.70`×1, `39777.78`×1

### `db2:strans_tmp.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `1132000.00`×1, `353333.33`×1, `747703.70`×1, `247111.11`×1, `72888.89`×1, `52592.59`×1, `27777.78`×1, `26080.00`×1

### `db2:suspend.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.VAT_AMT`
- Null rate trong sample: 0%
- Distinct ≈11; top: `0.00`×9, `10192.00`×2, `1000.00`×1, `60155.52`×1, `281999.99`×1, `364054.81`×1, `644000.00`×1, `42189.60`×1

## Ghi chú thêm

- Tiền thuế VAT
