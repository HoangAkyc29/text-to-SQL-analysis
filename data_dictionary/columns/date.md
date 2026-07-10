---
semantic_key: date
title: date
display_names:
- DATE
kind: date
tables:
- ref: db2:hisrtpr
  column: DATE
  type: datetime
- ref: db2:hissppr
  column: DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# date

**Semantic key:** `date` · **Cột vật lý:** `DATE`

## Ý nghĩa nghiệp vụ

Mốc thời gian (date) — dùng trong bảng HISRTPR, bảng HISSPPR.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:hisrtpr` | `DATE` | datetime | Mốc thời gian (date) trên bảng hisrtpr |
| `db2:hissppr` | `DATE` | datetime | Mốc thời gian (date) trên bảng hissppr |
