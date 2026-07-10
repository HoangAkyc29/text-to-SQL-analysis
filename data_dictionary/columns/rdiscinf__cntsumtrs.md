---
semantic_key: rdiscinf__cntsumtrs
title: Cntsumtrs (RDISCINF)
display_names:
- CNTSUMTRS
kind: measure
tables:
- ref: db2:rdiscinf
  column: CNTSUMTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cntsumtrs (RDISCINF)

**Semantic key:** `rdiscinf__cntsumtrs` · **Cột vật lý:** `CNTSUMTRS`

## Ý nghĩa nghiệp vụ

Tổng số lần KM đã cộng dồn (counter).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CNTSUMTRS` | numeric | Chỉ số đo lường (cntsumtrs) trên rule khuyến mãi / chiết khấu |
