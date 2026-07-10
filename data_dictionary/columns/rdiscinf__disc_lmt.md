---
semantic_key: rdiscinf__disc_lmt
title: Disc Lmt (RDISCINF)
display_names:
- DISC_LMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: DISC_LMT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Disc Lmt (RDISCINF)

**Semantic key:** `rdiscinf__disc_lmt` · **Cột vật lý:** `DISC_LMT`

## Ý nghĩa nghiệp vụ

Giới hạn mức chiết khấu tối đa (%) hoặc trần theo rule.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `DISC_LMT` | numeric | Chỉ số đo lường (disc lmt) trên rule khuyến mãi / chiết khấu |
