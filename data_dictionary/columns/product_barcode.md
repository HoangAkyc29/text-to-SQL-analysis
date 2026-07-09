---
semantic_key: product_barcode
title: Barcode quét POS — join BARCODE ↔ SKU_DEF
display_names:
- BARCODE
kind: identifier
tables:
- ref: db2:barcode
  column: BARCODE
  type: char
- ref: db2:sku_def
  column: BARCODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã vạch
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:barcode.BARCODE: top=4903015153500(1), 3008751188494(1), 8809022087226(1),
  5410976080428(1), 4005808305773(1)'
- 'db2:sku_def.BARCODE: top=8855529930015(1), 8935072620264(1), 5410376822918(1),
  8850222235061(1), 0088331418573(1)'
---

# Barcode quét POS — join BARCODE ↔ SKU_DEF

**Semantic key:** `product_barcode` · **Cột vật lý:** `BARCODE`

## Ý nghĩa nghiệp vụ

Barcode EAN/GTIN trên BARCODE — quét POS. Sample: 13 chữ số, ISDEFAULT flag. Join SKU_ID ↔ STRANS qua lookup SKU_DEF.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:barcode` | `BARCODE` | char | có dữ liệu |
| `db2:sku_def` | `BARCODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:barcode.BARCODE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `7622201704223`×1, `]C18934889110`×1, `0001700012214`×1, `0010044500411`×1, `0010181025358`×1, `0010181025853`×1, `0010181040313`×1, `0010181041587`×1

### `db2:sku_def.BARCODE`
- Null rate trong sample: 95%
- Distinct ≈1; top: `8938514975250`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã vạch
