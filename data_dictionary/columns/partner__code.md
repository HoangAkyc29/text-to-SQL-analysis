---
semantic_key: partner__code
title: Code (PARTNER)
display_names:
- CODE
kind: text
tables:
- ref: db2:partner
  column: CODE
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Code (PARTNER)

**Semantic key:** `partner__code` · **Cột vật lý:** `CODE`

## Ý nghĩa nghiệp vụ

Thuộc tính code — đối tác / khách B2B.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `CODE` | varchar | Thuộc tính code trên đối tác / khách B2B |
