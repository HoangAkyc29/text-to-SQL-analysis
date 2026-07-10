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
- column_semantic_registry
- business_prose
---

# Mã SKU hiển thị (user thường nhập thiếu số 0)

**Semantic key:** `product_display_sku_code` · **Cột vật lý:** `SKU_CODE`

## Ý nghĩa nghiệp vụ

Mã sku hiển thị (thường 8 chữ số, có thể thiếu số 0 đầu) — master sản phẩm (SKU).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `SKU_CODE` | varchar | Mã SKU hiển thị |

## Join

Thường join: `TRANS_NUM`
