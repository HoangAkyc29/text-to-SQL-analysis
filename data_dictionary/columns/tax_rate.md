---
semantic_key: tax_rate
title: Thuế suất (TAX_RATE)
display_names:
- TAX_RATE
kind: measure
tables:
- ref: db2:asso_inf
  column: TAX_RATE
  type: numeric
- ref: db2:ctrans
  column: TAX_RATE
  type: numeric
- ref: db2:sku_def
  column: TAX_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Thuế suất
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Thuế suất (TAX_RATE)

**Semantic key:** `tax_rate` · **Cột vật lý:** `TAX_RATE`

## Ý nghĩa nghiệp vụ

Thuế suất GTGT (%) áp dụng cho dòng hoặc chứng từ — dùng cùng VAT_AMT để kiểm tra tính thuế.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `TAX_RATE` | numeric | Thuế suất |
| `db2:ctrans` | `TAX_RATE` | numeric | Thuế suất |
| `db2:sku_def` | `TAX_RATE` | numeric | Thuế suất |
