---
semantic_key: rdiscinf__cardexcl
title: Cardexcl (RDISCINF)
display_names:
- CARDEXCL
kind: flag
tables:
- ref: db2:rdiscinf
  column: CARDEXCL
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cardexcl (RDISCINF)

**Semantic key:** `rdiscinf__cardexcl` · **Cột vật lý:** `CARDEXCL`

## Ý nghĩa nghiệp vụ

Cờ loại trừ thẻ — rule không áp dụng cho loại thẻ trong danh sách loại trừ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CARDEXCL` | bit | Cờ / trạng thái (cardexcl) trên rule khuyến mãi / chiết khấu |
