---
semantic_key: rdiscinf__maxdisctrs
title: Maxdisctrs (RDISCINF)
display_names:
- MAXDISCTRS
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXDISCTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Maxdisctrs (RDISCINF)

**Semantic key:** `rdiscinf__maxdisctrs` · **Cột vật lý:** `MAXDISCTRS`

## Ý nghĩa nghiệp vụ

Trần số lần KM tối đa mỗi khách / mỗi bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MAXDISCTRS` | numeric | Chỉ số đo lường (maxdisctrs) trên rule khuyến mãi / chiết khấu |
