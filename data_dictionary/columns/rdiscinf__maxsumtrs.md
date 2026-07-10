---
semantic_key: rdiscinf__maxsumtrs
title: Maxsumtrs (RDISCINF)
display_names:
- MAXSUMTRS
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXSUMTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Maxsumtrs (RDISCINF)

**Semantic key:** `rdiscinf__maxsumtrs` · **Cột vật lý:** `MAXSUMTRS`

## Ý nghĩa nghiệp vụ

Trần số lần áp dụng rule trên tổng chương trình.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MAXSUMTRS` | numeric | Chỉ số đo lường (maxsumtrs) trên rule khuyến mãi / chiết khấu |
