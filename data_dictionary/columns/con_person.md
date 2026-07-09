---
semantic_key: con_person
title: con person
display_names:
- CON_PERSON
kind: text
tables:
- ref: db2:partner
  column: CON_PERSON
  type: varchar
- ref: db2:supplier
  column: CON_PERSON
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột CON_PERSON
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:partner.CON_PERSON: top=Duy Thanh(1), Cty Ch©u ¢u VN(1), Cty Duy Thanh(1),
  Cty Toµn Quèc(1), Cty Minh Anh(1)'
- 'db2:supplier.CON_PERSON: top=Cty Siªu VÜ(1), Cty Long Shin(1), Cty Minh Anh(1),
  TrÇn Hoµ HiÒn(1), Cty Minh Ch­¬ng(1)'
---

# con person

**Semantic key:** `con_person` · **Cột vật lý:** `CON_PERSON`

## Ý nghĩa nghiệp vụ

Cột CON_PERSON trên PARTNER, SUPPLIER. db2:partner: top ViÖt Th¸i Ph¸t, An Ti, Toµn Gia HiÖp Ph­íc; db2:supplier: top ViÖt Th¸i Ph¸t, An Ti, Toµn Gia HiÖp Ph­íc.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `CON_PERSON` | varchar | có dữ liệu |
| `db2:supplier` | `CON_PERSON` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.CON_PERSON`
- Null rate trong sample: 35%
- Distinct ≈13; top: `ViÖt Th¸i Ph¸t`×1, `An Ti`×1, `Toµn Gia HiÖp Ph­íc`×1, `Cty Ch©u ¢u VN`×1, `Cty d­îc §µ N½ng`×1, `NguyÔn V¨n Thiªng`×1, `CTy V¹n H­¬ng`×1, `Cty Nguyªn Vò`×1

### `db2:supplier.CON_PERSON`
- Null rate trong sample: 35%
- Distinct ≈13; top: `ViÖt Th¸i Ph¸t`×1, `An Ti`×1, `Toµn Gia HiÖp Ph­íc`×1, `Cty Ch©u ¢u VN`×1, `Cty d­îc §µ N½ng`×1, `NguyÔn V¨n Thiªng`×1, `CTy V¹n H­¬ng`×1, `Cty Nguyªn Vò`×1

## Ghi chú thêm

