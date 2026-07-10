---
semantic_key: sku_def__tax_drate
title: Tax Drate (SKU_DEF)
display_names:
- TAX_DRATE
kind: measure
tables:
- ref: db2:sku_def
  column: TAX_DRATE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tax Drate (SKU_DEF)

**Semantic key:** `sku_def__tax_drate` · **Cột vật lý:** `TAX_DRATE`

## Ý nghĩa nghiệp vụ

Thuế suất giảm / đặc biệt (nếu có) trên master SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `TAX_DRATE` | numeric | Chỉ số đo lường (tax drate) trên master sản phẩm (SKU) |
