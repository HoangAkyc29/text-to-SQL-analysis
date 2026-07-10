---
semantic_key: inv_iss__gua_id
title: Mã định danh (gua id) (INV_ISS)
display_names:
- Gua_ID
kind: identifier
tables:
- ref: db2:inv_iss
  column: Gua_ID
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (gua id) (INV_ISS)

**Semantic key:** `inv_iss__gua_id` · **Cột vật lý:** `Gua_ID`

## Ý nghĩa nghiệp vụ

Mã định danh (gua id) — phiếu xuất kho.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `Gua_ID` | char | Mã định danh (gua id) trên phiếu xuất kho |
