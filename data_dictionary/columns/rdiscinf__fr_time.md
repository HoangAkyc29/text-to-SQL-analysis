---
semantic_key: rdiscinf__fr_time
title: Giờ fr (RDISCINF)
display_names:
- FR_TIME
kind: measure
tables:
- ref: db2:rdiscinf
  column: FR_TIME
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giờ fr (RDISCINF)

**Semantic key:** `rdiscinf__fr_time` · **Cột vật lý:** `FR_TIME`

## Ý nghĩa nghiệp vụ

Giờ bắt đầu áp dụng rule trong ngày (khung giờ KM).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `FR_TIME` | numeric | Giờ fr trên rule khuyến mãi / chiết khấu |
