---
semantic_key: rdiscinf__disc_frb
title: Disc Frb (RDISCINF)
display_names:
- DISC_FRB
kind: flag
tables:
- ref: db2:rdiscinf
  column: DISC_FRB
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Disc Frb (RDISCINF)

**Semantic key:** `rdiscinf__disc_frb` · **Cột vật lý:** `DISC_FRB`

## Ý nghĩa nghiệp vụ

Cờ chiết khấu forbidden / loại trừ một số hình thức KM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `DISC_FRB` | bit | Cờ / trạng thái (disc frb) trên rule khuyến mãi / chiết khấu |
