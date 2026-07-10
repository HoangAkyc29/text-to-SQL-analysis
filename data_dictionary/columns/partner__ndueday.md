---
semantic_key: partner__ndueday
title: Ndueday (PARTNER)
display_names:
- NDUEDAY
kind: measure
tables:
- ref: db2:partner
  column: NDUEDAY
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ndueday (PARTNER)

**Semantic key:** `partner__ndueday` · **Cột vật lý:** `NDUEDAY`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (ndueday) — đối tác / khách B2B.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:partner` | `NDUEDAY` | numeric | Chỉ số đo lường (ndueday) trên đối tác / khách B2B |
