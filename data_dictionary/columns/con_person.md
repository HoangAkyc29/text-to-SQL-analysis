---
semantic_key: con_person
title: Người liên hệ (CON_PERSON)
display_names:
- CON_PERSON
kind: text
tables:
- ref: db2:partner
  column: CON_PERSON
  type: varchar
- ref: db2:supplier
  column: CON_PERSON
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Người liên hệ (CON_PERSON)

**Semantic key:** `con_person` · **Cột vật lý:** `CON_PERSON`

## Ý nghĩa nghiệp vụ

Người liên hệ — dùng trong Master / danh mục (PARTNER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `CON_PERSON` | varchar | Người liên hệ trên đối tác / khách B2B |
| `db2:supplier` | `CON_PERSON` | varchar | Người liên hệ trên master nhà cung cấp |
