---
semantic_key: base_unit
title: base unit
display_names:
- BASE_UNIT
kind: text
tables:
- ref: db1:strans
  column: BASE_UNIT
  type: char
- ref: db2:asso_inf
  column: BASE_UNIT
  type: char
- ref: db2:hisrtpr
  column: BASE_UNIT
  type: char
- ref: db2:hissppr
  column: BASE_UNIT
  type: char
- ref: db2:st_order
  column: BASE_UNIT
  type: char
- ref: db2:strans
  column: BASE_UNIT
  type: char
- ref: db2:strans_tmp
  column: BASE_UNIT
  type: char
- ref: db2:suspend
  column: BASE_UNIT
  type: char
join_with: []
related_semantic_keys: []
facts:
- Đơn vị cơ sở
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.BASE_UNIT: top=KG(253), GOI(239), HOP(118), CAI(81), KHA(76)'
- 'db2:asso_inf.BASE_UNIT: top=KG(281), KHA(280), GOI(137), HOP(95), CHA(63)'
- 'db2:hisrtpr.BASE_UNIT: top=KG(263), CAI(246), GOI(158), HOP(114), CHA(82)'
- 'db2:hissppr.BASE_UNIT: top=CAI(254), GOI(172), HOP(132), KG(131), KHA(92)'
- 'db2:st_order.BASE_UNIT: top=CAI(269), GOI(252), CHA(131), HOP(114), BAO(86)'
- 'db2:strans.BASE_UNIT: top=KG(274), GOI(199), CAI(128), HOP(99), CHA(72)'
- 'db2:strans_tmp.BASE_UNIT: top=KG(275), GOI(245), HOP(118), KHA(89), CHA(61)'
- 'db2:suspend.BASE_UNIT: top=GOI(251), KG(241), HOP(129), CHA(82), KHA(71)'
---

# base unit

**Semantic key:** `base_unit` · **Cột vật lý:** `BASE_UNIT`

## Ý nghĩa nghiệp vụ

Cột BASE_UNIT trên ASSO_INF, HISRTPR, HISSPPR. db1:strans: top CAI, DOI, GOI; db2:asso_inf: top GOI, KG, KHA; db2:hisrtpr: top CAI, KHA, KG; db2:hissppr: top CHA, GOI, HOP; db2:st_order: top GOI, CHA, BAO; db2:strans: top CAI, BO, HOP; db2:strans_tmp: top HOP, CHA, GOI; db2:suspend: top CHA, KG, BAO.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `BASE_UNIT` | char | có dữ liệu |
| `db2:asso_inf` | `BASE_UNIT` | char | có dữ liệu |
| `db2:hisrtpr` | `BASE_UNIT` | char | có dữ liệu |
| `db2:hissppr` | `BASE_UNIT` | char | có dữ liệu |
| `db2:st_order` | `BASE_UNIT` | char | có dữ liệu |
| `db2:strans` | `BASE_UNIT` | char | có dữ liệu |
| `db2:strans_tmp` | `BASE_UNIT` | char | có dữ liệu |
| `db2:suspend` | `BASE_UNIT` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈5; top: `CAI`×10, `DOI`×5, `GOI`×3, `VI`×1, `HOP`×1

### `db2:asso_inf.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈7; top: `GOI`×5, `KG`×3, `KHA`×3, `HOP`×3, `BAO`×3, `LOC`×2, `CHA`×1

### `db2:hisrtpr.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈5; top: `CAI`×8, `KHA`×6, `KG`×3, `BAO`×2, `HOP`×1

### `db2:hissppr.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈4; top: `CHA`×9, `GOI`×7, `HOP`×3, `CAI`×1

### `db2:st_order.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈3; top: `GOI`×8, `CHA`×6, `BAO`×6

### `db2:strans.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈7; top: `CAI`×11, `BO`×3, `HOP`×2, `KG`×1, `CAN`×1, `GOI`×1, `DOI`×1

### `db2:strans_tmp.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈6; top: `HOP`×8, `CHA`×4, `GOI`×4, `LOC`×2, `BAO`×1, `LON`×1

### `db2:suspend.BASE_UNIT`
- Null rate trong sample: 0%
- Distinct ≈7; top: `CHA`×6, `KG`×5, `BAO`×3, `LOC`×3, `KHA`×1, `GOI`×1, `HOP`×1

## Ghi chú thêm

- Đơn vị cơ sở
