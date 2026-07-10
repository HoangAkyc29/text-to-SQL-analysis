---
semantic_key: sku_def__lbl_type
title: Lbl Type (SKU_DEF)
display_names:
- LBL_TYPE
kind: text
tables:
- ref: db2:sku_def
  column: LBL_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Lbl Type (SKU_DEF)

**Semantic key:** `sku_def__lbl_type` · **Cột vật lý:** `LBL_TYPE`

## Ý nghĩa nghiệp vụ

Loại nhãn in (tem, shelf talker, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `LBL_TYPE` | char | Thuộc tính lbl type trên master sản phẩm (SKU) |
