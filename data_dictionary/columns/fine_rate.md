---
semantic_key: fine_rate
title: fine rate
display_names:
- fine_rate
- FINE_RATE
kind: measure
tables:
- ref: db2:partner
  column: fine_rate
  type: numeric
- ref: db2:supplier
  column: FINE_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệFINE_RATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# fine rate

**Semantic key:** `fine_rate` · **Cột vật lý:** `fine_rate`, `FINE_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệFINE_RATE. Dùng trong Master / danh mục (PARTNER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `fine_rate` | numeric | Tỷ lệ phạt (%) trên đối tác / khách B2B |
| `db2:supplier` | `FINE_RATE` | numeric | Tỷ lệFINE_RATE |
