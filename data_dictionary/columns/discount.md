---
semantic_key: discount
title: discount
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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.DISCOUNT: top=0.00(787), 2700.00(2), 3474.80(1), 15362.00(1),
  14054.00(1)'
- 'db1:strans.DISCOUNT: top=0.00(984), 30000.00(2), 1500.00(2), 16000.00(1), 5000.00(1)'
- 'db1:transhdr_arc.DISCOUNT: top=0.00(939), 1000.00(3), 1500.00(2), 2000.00(2), 3500.00(2)'
- 'db2:crdtrans.DISCOUNT: top=0.00(1000)'
- 'db2:crdtrans_tmp.DISCOUNT: top=0.00(1000)'
- 'db2:inv_hdr.DISCOUNT: top=0.00(810), 62858.88(2), 96000.00(2), 410454.55(1), 161220.00(1)'
- 'db2:inv_iss.DISCOUNT: top=0.00(1000)'
- 'db2:partner.DISCOUNT: top=0.00(1000)'
- 'db2:st_order.DISCOUNT: top=0.00(1000)'
- 'db2:strans.DISCOUNT: top=0.00(998), 74640.00(1), 96048.00(1)'
- 'db2:strans_tmp.DISCOUNT: top=0.00(993), 16000.00(1), 5000.00(1), 8100.00(1), 20616.00(1)'
- 'db2:suspend.DISCOUNT: top=0.00(990), 3000.00(2), 32016.00(1), 5200.00(1), 14000.00(1)'
- 'db2:transhdr.DISCOUNT: top=0.00(987), 32886.00(1), 22077.00(1), 156406.71(1), 26016.00(1)'
---

# discount

**Semantic key:** `discount` · **Cột vật lý:** `DISCOUNT`

## Ý nghĩa nghiệp vụ

Cột DISCOUNT trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db1:strans: top 0.00; db1:transhdr_arc: top 0.00, 2000.00; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00; db2:inv_hdr: top 0.00, 250887.08, 406114.50; db2:inv_iss: top 0.00; db2:partner: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00, 1526000.00, 133000.01; db2:strans_tmp: top 0.00; db2:suspend: top 0.00; db2:transhdr: top 0.00, 1847611.13, 159904.03.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `DISCOUNT` | numeric | có dữ liệu |
| `db1:strans` | `DISCOUNT` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:crdtrans` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:inv_hdr` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:inv_iss` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:partner` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:st_order` | `DISCOUNT` | decimal | có dữ liệu |
| `db2:strans` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:suspend` | `DISCOUNT` | numeric | có dữ liệu |
| `db2:transhdr` | `DISCOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db1:strans.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db1:transhdr_arc.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.00`×19, `2000.00`×1

### `db2:crdtrans.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:inv_hdr.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0.00`×18, `250887.08`×1, `406114.50`×1

### `db2:inv_iss.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:partner.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈6; top: `0.00`×15, `1526000.00`×1, `133000.01`×1, `36944.45`×1, `56388.89`×1, `38888.89`×1

### `db2:strans_tmp.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.DISCOUNT`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0.00`×18, `1847611.13`×1, `159904.03`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Giảm giá (số tiền hoặc % tùy ngữ cảnh)
