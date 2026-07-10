---
semantic_key: fax
title: fax
display_names:
- FAX
kind: text
tables:
- ref: db2:partner
  column: FAX
  type: varchar
- ref: db2:supplier
  column: FAX
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# fax

**Semantic key:** `fax` · **Cột vật lý:** `FAX`

## Ý nghĩa nghiệp vụ

Thuộc tính fax — dùng trong Master / danh mục (PARTNER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `FAX` | varchar | Thuộc tính fax trên đối tác / khách B2B |
| `db2:supplier` | `FAX` | varchar | Thuộc tính fax trên master nhà cung cấp |
