---
semantic_key: sale_line_sku_id
title: Mã SKU trên dòng bán — join SKU_DEF
display_names:
- SKU_ID
kind: identifier
tables:
- ref: db1:strans
  column: SKU_ID
  type: char
- ref: db2:strans
  column: SKU_ID
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã sản phẩm nội bộ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.SKU_ID: top=290300472100(12), 290300471500(9), 290312296400(6), 290612847900(6),
  290300003500(6)'
- 'db2:strans.SKU_ID: top=290002963500(29), 290002963400(23), 290002963600(16), 290002963300(15),
  290001381800(10)'
---

# Mã SKU trên dòng bán — join SKU_DEF

**Semantic key:** `sale_line_sku_id` · **Cột vật lý:** `SKU_ID`

## Ý nghĩa nghiệp vụ

SKU_ID trên dòng STRANS — join SKU_DEF/BARCODE để lọc quà tặng, hàng KM. User thường nhập SKU_CODE 8 số; trong DB là mã nội bộ 290…

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `SKU_ID` | char | Join SKU_DEF — lọc quà/KM |
| `db2:strans` | `SKU_ID` | char | Join SKU_DEF — lọc quà/KM |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290001866600`×1, `290002870100`×1, `290002869600`×1, `290002869900`×1, `290002875100`×1, `290002432900`×1, `290002844400`×1, `290002298000`×1

### `db2:strans.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290002973000`×1, `290002870000`×1, `290002870100`×1, `290002868600`×1, `290002875100`×1, `290002341600`×1, `290002341700`×1, `290002958900`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã sản phẩm nội bộ
