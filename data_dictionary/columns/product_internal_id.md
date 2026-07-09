---
semantic_key: product_internal_id
title: Mã sản phẩm nội bộ SKU_ID
display_names:
- SKU_ID
kind: identifier
tables:
- ref: db2:barcode
  column: SKU_ID
  type: char
- ref: db2:sku_def
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
- 'db2:barcode.SKU_ID: top=290112027600(3), 290110899500(3), 290111218900(3), 290112316600(3),
  290610735800(2)'
- 'db2:sku_def.SKU_ID: top=290212804400(1), 290400422200(1), 290001061400(1), 290600206600(1),
  290212918000(1)'
---

# Mã sản phẩm nội bộ SKU_ID

**Semantic key:** `product_internal_id` · **Cột vật lý:** `SKU_ID`

## Ý nghĩa nghiệp vụ

SKU_ID nội bộ (290…). Join STRANS ↔ SKU_DEF. Khác user-facing SKU_CODE (8 chữ số).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:barcode` | `SKU_ID` | char | có dữ liệu |
| `db2:sku_def` | `SKU_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:barcode.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈17; top: `290002608000`×3, `290001865200`×2, `290002607300`×1, `290110926600`×1, `290112681000`×1, `290002075000`×1, `290112526700`×1, `290112161100`×1

### `db2:sku_def.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290000000100`×1, `290000000200`×1, `290000000300`×1, `290000000400`×1, `290000000500`×1, `290000000600`×1, `290000000700`×1, `290000000800`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã sản phẩm nội bộ
