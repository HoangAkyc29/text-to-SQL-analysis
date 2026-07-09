---
semantic_key: product_display_sku_code
title: Mã SKU hiển thị (user thường nhập thiếu số 0)
display_names:
- SKU_CODE
kind: code
tables:
- ref: db2:sku_def
  column: SKU_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã SKU hiển thị
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:sku_def.SKU_CODE: top=02128044(1), 0404004222(1), 00010614(1), 0606002066(1),
  02129180(1)'
---

# Mã SKU hiển thị (user thường nhập thiếu số 0)

**Semantic key:** `product_display_sku_code` · **Cột vật lý:** `SKU_CODE`

## Ý nghĩa nghiệp vụ

Cột SKU_CODE trên SKU_DEF. db2:sku_def: top 00000001, 00000002, 00000003.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `SKU_CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.SKU_CODE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00000001`×1, `00000002`×1, `00000003`×1, `00000004`×1, `00000005`×1, `00003536`×1, `00000007`×1, `00000008`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã SKU hiển thị
