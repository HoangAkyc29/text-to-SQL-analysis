---
semantic_key: suspend__dmdisc
title: Dmdisc (SUSPEND)
display_names:
- DMDISC
kind: flag
tables:
- ref: db2:suspend
  column: DMDISC
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Dmdisc (SUSPEND)

**Semantic key:** `suspend__dmdisc` · **Cột vật lý:** `DMDISC`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (dmdisc) — bill đang treo / chưa hoàn tất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:suspend` | `DMDISC` | bit | Cờ / trạng thái (dmdisc) trên bill đang treo / chưa hoàn tất |
