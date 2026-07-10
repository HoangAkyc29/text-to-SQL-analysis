---
semantic_key: cash_denomination_value
title: cash denomination value
display_names:
- VALUE
kind: measure
tables:
- ref: db2:cash_st
  column: VALUE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Mệnh giá tờ tiền (200, 500, 1000, … VND)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# cash denomination value

**Semantic key:** `cash_denomination_value` · **Cột vật lý:** `VALUE`

## Ý nghĩa nghiệp vụ

Mệnh giá tờ tiền (200, 500, 1000, … VND) (ngữ cảnh: quỹ tiền mặt theo mệnh giá).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cash_st` | `VALUE` | numeric | Mệnh giá tờ tiền (200, 500, 1000, … VND) |
