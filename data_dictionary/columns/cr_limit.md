---
semantic_key: cr_limit
title: Hạn mức công nợ (CR_LIMIT)
display_names:
- CR_LIMIT
kind: measure
tables:
- ref: db2:account
  column: CR_LIMIT
  type: numeric
- ref: db2:partner
  column: CR_LIMIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Hạn mức tín dụng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Hạn mức công nợ (CR_LIMIT)

**Semantic key:** `cr_limit` · **Cột vật lý:** `CR_LIMIT`

## Ý nghĩa nghiệp vụ

Hạn mức tín dụng. Dùng trong Master / danh mục (PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `CR_LIMIT` | numeric | Hạn mức tín dụng |
| `db2:partner` | `CR_LIMIT` | numeric | Hạn mức tín dụng |
