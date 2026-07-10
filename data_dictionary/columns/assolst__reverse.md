---
semantic_key: assolst__reverse
title: Reverse (ASSOLST)
display_names:
- REVERSE
kind: flag
tables:
- ref: db2:assolst
  column: REVERSE
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Reverse (ASSOLST)

**Semantic key:** `assolst__reverse` · **Cột vật lý:** `REVERSE`

## Ý nghĩa nghiệp vụ

Cờ combo reverse — đảo chiều quy tắc gộp (bundle ngược / unbundle).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:assolst` | `REVERSE` | bit | Cờ / trạng thái (reverse) trên master combo / bundle |
