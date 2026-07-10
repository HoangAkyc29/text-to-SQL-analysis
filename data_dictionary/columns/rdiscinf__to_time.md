---
semantic_key: rdiscinf__to_time
title: Giờ to (RDISCINF)
display_names:
- TO_TIME
kind: measure
tables:
- ref: db2:rdiscinf
  column: TO_TIME
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giờ to (RDISCINF)

**Semantic key:** `rdiscinf__to_time` · **Cột vật lý:** `TO_TIME`

## Ý nghĩa nghiệp vụ

Giờ kết thúc áp dụng rule trong ngày.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `TO_TIME` | numeric | Giờ to trên rule khuyến mãi / chiết khấu |
