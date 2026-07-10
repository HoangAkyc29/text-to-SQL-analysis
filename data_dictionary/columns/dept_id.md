---
semantic_key: dept_id
title: Mã ngành hàng (merchandise department)
display_names:
- DEPT_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: DEPT_ID
  type: char
- ref: db2:supplier
  column: DEPT_ID
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã ngành hàng (merchandise department)

**Semantic key:** `dept_id` · **Cột vật lý:** `DEPT_ID`

## Ý nghĩa nghiệp vụ

Mã ngành hàng / phòng ban merchandise — phân loại SKU và nhà cung cấp theo cây ngành hàng nội bộ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `DEPT_ID` | char | ngành hàng của SKU trong cây phân loại hàng hóa |
| `db2:supplier` | `DEPT_ID` | char | ngành hàng mặc định gắn với nhà cung cấp |
