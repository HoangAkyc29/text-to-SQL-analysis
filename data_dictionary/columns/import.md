---
semantic_key: import
title: Cờ hàng nhập khẩu (IMPORT)
display_names:
- IMPORT
kind: flag
tables:
- ref: db1:strans
  column: IMPORT
  type: bit
- ref: db2:asso_inf
  column: IMPORT
  type: bit
- ref: db2:custhist
  column: IMPORT
  type: bit
- ref: db2:st_order
  column: IMPORT
  type: bit
- ref: db2:strans
  column: IMPORT
  type: bit
- ref: db2:strans_tmp
  column: IMPORT
  type: bit
- ref: db2:suspend
  column: IMPORT
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cờ nhập / import
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ hàng nhập khẩu (IMPORT)

**Semantic key:** `import` · **Cột vật lý:** `IMPORT`

## Ý nghĩa nghiệp vụ

Cờ nhập / import. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `IMPORT` | bit | Cờ nhập / import |
| `db2:asso_inf` | `IMPORT` | bit | Cờ nhập / import |
| `db2:custhist` | `IMPORT` | bit | Cờ nhập / import |
| `db2:st_order` | `IMPORT` | bit | Cờ nhập / import |
| `db2:strans` | `IMPORT` | bit | Cờ nhập / import |
| `db2:strans_tmp` | `IMPORT` | bit | Cờ nhập / import |
| `db2:suspend` | `IMPORT` | bit | Cờ nhập / import |
