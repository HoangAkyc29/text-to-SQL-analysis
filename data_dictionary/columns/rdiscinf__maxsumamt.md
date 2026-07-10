---
semantic_key: rdiscinf__maxsumamt
title: Maxsumamt (RDISCINF)
display_names:
- MAXSUMAMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXSUMAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Maxsumamt (RDISCINF)

**Semantic key:** `rdiscinf__maxsumamt` · **Cột vật lý:** `MAXSUMAMT`

## Ý nghĩa nghiệp vụ

Trần tổng tiền chiết khấu / quà tối đa cho cả rule.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MAXSUMAMT` | numeric | Chỉ số đo lường (maxsumamt) trên rule khuyến mãi / chiết khấu |
