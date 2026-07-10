---
semantic_key: rdiscinf__maxsumqty
title: Maxsumqty (RDISCINF)
display_names:
- MAXSUMQTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXSUMQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Maxsumqty (RDISCINF)

**Semantic key:** `rdiscinf__maxsumqty` · **Cột vật lý:** `MAXSUMQTY`

## Ý nghĩa nghiệp vụ

Trần tổng số lượng quà / hàng KM tối đa cho cả rule.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MAXSUMQTY` | numeric | Chỉ số đo lường (maxsumqty) trên rule khuyến mãi / chiết khấu |
