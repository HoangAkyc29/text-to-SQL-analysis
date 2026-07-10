---
semantic_key: rdiscinf__cardrq
title: Cardrq (RDISCINF)
display_names:
- CARDRQ
kind: flag
tables:
- ref: db2:rdiscinf
  column: CARDRQ
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cardrq (RDISCINF)

**Semantic key:** `rdiscinf__cardrq` · **Cột vật lý:** `CARDRQ`

## Ý nghĩa nghiệp vụ

Cờ bắt buộc quét thẻ loyalty để rule KM có hiệu lực.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CARDRQ` | bit | Cờ / trạng thái (cardrq) trên rule khuyến mãi / chiết khấu |
