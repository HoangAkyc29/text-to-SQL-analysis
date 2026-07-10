---
semantic_key: lastrtpr
title: lastrtpr
display_names:
- LASTRTPR
kind: measure
tables:
- ref: db2:hisrtpr
  column: LASTRTPR
  type: numeric
- ref: db2:plu
  column: LASTRTPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá bán lẻ gần nhất
sources:
- table_md
- column_semantic_registry
- business_prose
---

# lastrtpr

**Semantic key:** `lastrtpr` · **Cột vật lý:** `LASTRTPR`

## Ý nghĩa nghiệp vụ

Giá bán lẻ gần nhất. Dùng trong bảng HISRTPR, bảng PLU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:hisrtpr` | `LASTRTPR` | numeric | Giá bán lẻ gần nhất |
| `db2:plu` | `LASTRTPR` | numeric | Giá bán lẻ gần nhất |
