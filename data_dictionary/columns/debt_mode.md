---
semantic_key: debt_mode
title: debt mode
display_names:
- DEBT_MODE
kind: flag
tables:
- ref: db2:customer
  column: DEBT_MODE
  type: bit
- ref: db2:partner
  column: DEBT_MODE
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# debt mode

**Semantic key:** `debt_mode` · **Cột vật lý:** `DEBT_MODE`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (debt mode) — dùng trong Master / danh mục (CUSTOMER, PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `DEBT_MODE` | bit | Cờ / trạng thái (debt mode) trên danh mục master khách hàng |
| `db2:partner` | `DEBT_MODE` | bit | Cờ / trạng thái (debt mode) trên đối tác / khách B2B |
