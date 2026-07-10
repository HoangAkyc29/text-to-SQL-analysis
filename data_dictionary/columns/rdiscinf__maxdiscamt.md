---
semantic_key: rdiscinf__maxdiscamt
title: Maxdiscamt (RDISCINF)
display_names:
- MAXDISCAMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXDISCAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Maxdiscamt (RDISCINF)

**Semantic key:** `rdiscinf__maxdiscamt` · **Cột vật lý:** `MAXDISCAMT`

## Ý nghĩa nghiệp vụ

Trần tiền chiết khấu tối đa mỗi lần áp dụng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MAXDISCAMT` | numeric | Chỉ số đo lường (maxdiscamt) trên rule khuyến mãi / chiết khấu |
