---
semantic_key: action
title: Mã thao tác nghiệp vụ trên chứng từ (ACTION)
display_names:
- ACTION
kind: text
tables:
- ref: db2:ctrans
  column: ACTION
  type: char
- ref: db2:debt
  column: ACTION
  type: char
- ref: db2:st_order
  column: ACTION
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã thao tác
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã thao tác nghiệp vụ trên chứng từ (ACTION)

**Semantic key:** `action` · **Cột vật lý:** `ACTION`

## Ý nghĩa nghiệp vụ

Mã thao tác. Dùng trong Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `ACTION` | char | Mã thao tác |
| `db2:debt` | `ACTION` | char | Mã thao tác |
| `db2:st_order` | `ACTION` | char | Mã thao tác |
