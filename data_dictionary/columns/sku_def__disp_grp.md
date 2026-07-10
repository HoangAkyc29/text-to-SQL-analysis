---
semantic_key: sku_def__disp_grp
title: Disp Grp (SKU_DEF)
display_names:
- DISP_GRP
kind: measure
tables:
- ref: db2:sku_def
  column: DISP_GRP
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Disp Grp (SKU_DEF)

**Semantic key:** `sku_def__disp_grp` · **Cột vật lý:** `DISP_GRP`

## Ý nghĩa nghiệp vụ

Nhóm trưng bày (display group) trên kệ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `DISP_GRP` | numeric | Chỉ số đo lường (disp grp) trên master sản phẩm (SKU) |
