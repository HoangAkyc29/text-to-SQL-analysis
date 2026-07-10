---
semantic_key: time
title: time
display_names:
- TIME
kind: text
tables:
- ref: db2:hisrtpr
  column: TIME
  type: char
- ref: db2:hissppr
  column: TIME
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# time

**Semantic key:** `time` · **Cột vật lý:** `TIME`

## Ý nghĩa nghiệp vụ

Thuộc tính time — dùng trong bảng HISRTPR, bảng HISSPPR.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:hisrtpr` | `TIME` | char | Thuộc tính time trên bảng hisrtpr |
| `db2:hissppr` | `TIME` | char | Thuộc tính time trên bảng hissppr |
