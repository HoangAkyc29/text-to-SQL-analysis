---
semantic_key: mobi
title: mobi
display_names:
- MOBI
kind: text
tables:
- ref: db2:cscard
  column: MOBI
  type: varchar
- ref: db2:customer
  column: MOBI
  type: varchar
- ref: db2:partner
  column: MOBI
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Di động
sources:
- table_md
- column_semantic_registry
- business_prose
---

# mobi

**Semantic key:** `mobi` · **Cột vật lý:** `MOBI`

## Ý nghĩa nghiệp vụ

Di động. Dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (CUSTOMER, PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `MOBI` | varchar | Di động |
| `db2:customer` | `MOBI` | varchar | Di động |
| `db2:partner` | `MOBI` | varchar | Di động |
