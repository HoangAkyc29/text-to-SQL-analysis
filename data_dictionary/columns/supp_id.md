---
semantic_key: supp_id
title: supp id
display_names:
- SUPP_ID
kind: identifier
tables:
- ref: db1:strans
  column: SUPP_ID
  type: char
- ref: db1:transhdr_arc
  column: SUPP_ID
  type: char
- ref: db2:account
  column: SUPP_ID
  type: char
- ref: db2:hissppr
  column: SUPP_ID
  type: char
- ref: db2:sku_def
  column: SUPP_ID
  type: char
- ref: db2:strans
  column: SUPP_ID
  type: char
- ref: db2:supplier
  column: SUPP_ID
  type: char
- ref: db2:transhdr
  column: SUPP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã nhà cung cấp
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.SUPP_ID: top=50971(7), 50724(7), 00062(6), 50617(2), 50304(2)'
- 'db1:transhdr_arc.SUPP_ID: top=50240(3), 50426(3), 60260(2), 50871(1), 51170(1)'
- 'db2:account.SUPP_ID: top=60174(1), 00164(1), 51128(1), 51576(1), 00378(1)'
- 'db2:hissppr.SUPP_ID: top=50356(54), 50337(48), 50304(40), 50962(38), 50971(30)'
- 'db2:sku_def.SUPP_ID: top=50304(146), 50299(58), 50356(49), 50298(36), 50350(33)'
- 'db2:strans.SUPP_ID: top=50971(16), 50371(4), 50610(4), 51067(2), 51431(2)'
- 'db2:supplier.SUPP_ID: top=50204(1), 50760(1), 00714(1), 60144(1), 50614(1)'
- 'db2:transhdr.SUPP_ID: top=50371(3), 51454(3), 51451(2), 50971(2), 50747(2)'
---

# supp id

**Semantic key:** `supp_id` · **Cột vật lý:** `SUPP_ID`

## Ý nghĩa nghiệp vụ

Cột SUPP_ID trên ACCOUNT, HISSPPR, SKU_DEF. db1:strans: top 50565, 51550, 51547; db2:account: top 00004, 00006, 00010; db2:hissppr: top 00114, 00017, 50753; db2:sku_def: top 50356, 50337, 50947; db2:strans: top 50672, 50565, 51547; db2:supplier: top 00004, 00006, 00010; db2:transhdr: top 50747, 50855, 51547.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `SUPP_ID` | char | có dữ liệu |
| `db1:transhdr_arc` | `SUPP_ID` | char | có dữ liệu |
| `db2:account` | `SUPP_ID` | char | có dữ liệu |
| `db2:hissppr` | `SUPP_ID` | char | có dữ liệu |
| `db2:sku_def` | `SUPP_ID` | char | có dữ liệu |
| `db2:strans` | `SUPP_ID` | char | có dữ liệu |
| `db2:supplier` | `SUPP_ID` | char | có dữ liệu |
| `db2:transhdr` | `SUPP_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈4; top: `50565`×10, `51550`×5, `51547`×4, `51373`×1

### `db2:account.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

### `db2:hissppr.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈6; top: `00114`×7, `00017`×6, `50753`×4, `50298`×1, `50014`×1, `50794`×1

### `db2:sku_def.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈6; top: `50356`×12, `50337`×3, `50947`×2, `50984`×1, `50962`×1, `51221`×1

### `db2:strans.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈4; top: `50672`×8, `50565`×7, `51547`×4, `51067`×1

### `db2:supplier.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

### `db2:transhdr.SUPP_ID`
- Null rate trong sample: 0%
- Distinct ≈11; top: `50747`×6, `50855`×4, `51547`×2, `51067`×1, `50565`×1, `50672`×1, `51449`×1, `50426`×1

## Ghi chú thêm

- Mã nhà cung cấp
