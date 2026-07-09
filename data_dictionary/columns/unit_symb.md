---
semantic_key: unit_symb
title: unit symb
display_names:
- UNIT_SYMB
kind: text
tables:
- ref: db1:strans
  column: UNIT_SYMB
  type: char
- ref: db2:asso_inf
  column: UNIT_SYMB
  type: char
- ref: db2:barcode
  column: UNIT_SYMB
  type: char
- ref: db2:hisrtpr
  column: UNIT_SYMB
  type: char
- ref: db2:hissppr
  column: UNIT_SYMB
  type: char
- ref: db2:sku_def
  column: UNIT_SYMB
  type: char
- ref: db2:st_order
  column: UNIT_SYMB
  type: char
- ref: db2:strans
  column: UNIT_SYMB
  type: char
- ref: db2:strans_tmp
  column: UNIT_SYMB
  type: char
- ref: db2:suspend
  column: UNIT_SYMB
  type: char
join_with: []
related_semantic_keys: []
facts:
- Ký hiệu đơn vị (GOI, HOP, KG, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.UNIT_SYMB: top=KG(253), GOI(239), HOP(118), CAI(80), KHA(76)'
- 'db2:asso_inf.UNIT_SYMB: top=KHA(279), KG(272), GOI(137), HOP(95), CHA(63)'
- 'db2:barcode.UNIT_SYMB: top=GOI(234), CAI(223), CHA(190), HOP(170), BAO(33)'
- 'db2:hisrtpr.UNIT_SYMB: top=KG(263), CAI(246), GOI(158), HOP(114), CHA(82)'
- 'db2:hissppr.UNIT_SYMB: top=CAI(254), GOI(181), KG(131), HOP(131), CHA(89)'
- 'db2:sku_def.UNIT_SYMB: top=CAI(442), HOP(64), GOI(53), DOI(42), KHA(42)'
- 'db2:st_order.UNIT_SYMB: top=CAI(269), GOI(251), CHA(131), HOP(114), BAO(86)'
- 'db2:strans.UNIT_SYMB: top=KG(274), GOI(199), CAI(128), HOP(99), CHA(72)'
- 'db2:strans_tmp.UNIT_SYMB: top=KG(275), GOI(245), HOP(118), KHA(89), CHA(61)'
- 'db2:suspend.UNIT_SYMB: top=GOI(251), KG(241), HOP(129), CHA(82), KHA(71)'
---

# unit symb

**Semantic key:** `unit_symb` · **Cột vật lý:** `UNIT_SYMB`

## Ý nghĩa nghiệp vụ

Cột UNIT_SYMB trên ASSO_INF, BARCODE, HISRTPR. db1:strans: top CAI, DOI, GOI; db2:asso_inf: top GOI, KG, KHA; db2:barcode: top CHA, GOI, HOP; db2:hisrtpr: top CAI, KHA, KG; db2:hissppr: top CHA, GOI, HOP; db2:sku_def: top CAI, KHA, BAO; db2:st_order: top GOI, CHA, BAO; db2:strans: top CAI, BO, HOP; db2:strans_tmp: top HOP, CHA, GOI; db2:suspend: top CHA, KG, BAO.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:asso_inf` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:barcode` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:hisrtpr` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:hissppr` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:sku_def` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:st_order` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:strans` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:strans_tmp` | `UNIT_SYMB` | char | có dữ liệu |
| `db2:suspend` | `UNIT_SYMB` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈5; top: `CAI`×10, `DOI`×5, `GOI`×3, `VI`×1, `HOP`×1

### `db2:asso_inf.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈7; top: `GOI`×5, `KG`×3, `KHA`×3, `HOP`×3, `BAO`×3, `LOC`×2, `CHA`×1

### `db2:barcode.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈4; top: `CHA`×8, `GOI`×7, `HOP`×4, `HU`×1

### `db2:hisrtpr.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈5; top: `CAI`×8, `KHA`×6, `KG`×3, `BAO`×2, `HOP`×1

### `db2:hissppr.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈4; top: `CHA`×9, `GOI`×7, `HOP`×3, `DOI`×1

### `db2:sku_def.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈5; top: `CAI`×12, `KHA`×5, `BAO`×1, `HOP`×1, `KG`×1

### `db2:st_order.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈3; top: `GOI`×8, `CHA`×6, `BAO`×6

### `db2:strans.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈7; top: `CAI`×11, `BO`×3, `HOP`×2, `KG`×1, `CAN`×1, `GOI`×1, `DOI`×1

### `db2:strans_tmp.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈6; top: `HOP`×8, `CHA`×4, `GOI`×4, `LOC`×2, `BAO`×1, `LON`×1

### `db2:suspend.UNIT_SYMB`
- Null rate trong sample: 0%
- Distinct ≈7; top: `CHA`×6, `KG`×5, `BAO`×3, `LOC`×3, `KHA`×1, `GOI`×1, `HOP`×1

## Ghi chú thêm

- Ký hiệu đơn vị (GOI, HOP, KG, …)
