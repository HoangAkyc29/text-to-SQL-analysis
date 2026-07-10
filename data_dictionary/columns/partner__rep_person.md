---
semantic_key: partner__rep_person
title: Rep Person (PARTNER)
display_names:
- REP_PERSON
kind: text
tables:
- ref: db2:partner
  column: REP_PERSON
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Rep Person (PARTNER)

**Semantic key:** `partner__rep_person` · **Cột vật lý:** `REP_PERSON`

## Ý nghĩa nghiệp vụ

Thuộc tính rep person — đối tác / khách B2B.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `REP_PERSON` | varchar | Thuộc tính rep person trên đối tác / khách B2B |
