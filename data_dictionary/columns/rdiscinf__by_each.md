---
semantic_key: rdiscinf__by_each
title: By Each (RDISCINF)
display_names:
- BY_EACH
kind: flag
tables:
- ref: db2:rdiscinf
  column: BY_EACH
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# By Each (RDISCINF)

**Semantic key:** `rdiscinf__by_each` · **Cột vật lý:** `BY_EACH`

## Ý nghĩa nghiệp vụ

Cờ áp dụng theo từng đơn vị / từng dòng thay vì cả bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `BY_EACH` | bit | Cờ / trạng thái (by each) trên rule khuyến mãi / chiết khấu |
