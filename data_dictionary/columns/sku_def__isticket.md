---
semantic_key: sku_def__isticket
title: Cờ thuộc tính (ticket) (SKU_DEF)
display_names:
- IsTicket
kind: flag
tables:
- ref: db2:sku_def
  column: IsTicket
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (ticket) (SKU_DEF)

**Semantic key:** `sku_def__isticket` · **Cột vật lý:** `IsTicket`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (ticket) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsTicket` | bit | Cờ thuộc tính (ticket) trên master sản phẩm (SKU) |
