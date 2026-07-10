---
semantic_key: supplier__supp_name
title: Tên nhà cung cấp (SUPPLIER)
display_names:
- SUPP_NAME
kind: text
tables:
- ref: db2:supplier
  column: SUPP_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên nhà cung cấp
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tên nhà cung cấp (SUPPLIER)

**Semantic key:** `supplier__supp_name` · **Cột vật lý:** `SUPP_NAME`

## Ý nghĩa nghiệp vụ

Tên nhà cung cấp chính thức trên master SUPPLIER — dùng tra cứu và in chứng từ mua.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `SUPP_NAME` | nvarchar | Tên nhà cung cấp |
