---
semantic_key: rdiscinf__cntsumqty
title: Cntsumqty (RDISCINF)
display_names:
- CNTSUMQTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: CNTSUMQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cntsumqty (RDISCINF)

**Semantic key:** `rdiscinf__cntsumqty` · **Cột vật lý:** `CNTSUMQTY`

## Ý nghĩa nghiệp vụ

Tổng số lượng KM đã cộng dồn (counter).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CNTSUMQTY` | numeric | Chỉ số đo lường (cntsumqty) trên rule khuyến mãi / chiết khấu |
