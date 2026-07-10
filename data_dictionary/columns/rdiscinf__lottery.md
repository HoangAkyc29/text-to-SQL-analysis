---
semantic_key: rdiscinf__lottery
title: Lottery (RDISCINF)
display_names:
- LOTTERY
kind: flag
tables:
- ref: db2:rdiscinf
  column: LOTTERY
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Lottery (RDISCINF)

**Semantic key:** `rdiscinf__lottery` · **Cột vật lý:** `LOTTERY`

## Ý nghĩa nghiệp vụ

Cờ rule xổ số / quay thưởng gắn KM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `LOTTERY` | bit | Cờ / trạng thái (lottery) trên rule khuyến mãi / chiết khấu |
