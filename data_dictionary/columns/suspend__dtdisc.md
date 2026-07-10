---
semantic_key: suspend__dtdisc
title: Dtdisc (SUSPEND)
display_names:
- DTDISC
kind: flag
tables:
- ref: db2:suspend
  column: DTDISC
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Dtdisc (SUSPEND)

**Semantic key:** `suspend__dtdisc` · **Cột vật lý:** `DTDISC`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (dtdisc) — bill đang treo / chưa hoàn tất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:suspend` | `DTDISC` | bit | Cờ / trạng thái (dtdisc) trên bill đang treo / chưa hoàn tất |
