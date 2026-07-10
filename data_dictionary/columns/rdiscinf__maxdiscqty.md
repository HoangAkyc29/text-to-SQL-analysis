---
semantic_key: rdiscinf__maxdiscqty
title: Maxdiscqty (RDISCINF)
display_names:
- MAXDISCQTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXDISCQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Maxdiscqty (RDISCINF)

**Semantic key:** `rdiscinf__maxdiscqty` · **Cột vật lý:** `MAXDISCQTY`

## Ý nghĩa nghiệp vụ

Trần số lượng KM tối đa mỗi lần áp dụng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MAXDISCQTY` | numeric | Chỉ số đo lường (maxdiscqty) trên rule khuyến mãi / chiết khấu |
