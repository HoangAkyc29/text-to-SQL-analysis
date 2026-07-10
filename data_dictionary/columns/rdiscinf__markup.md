---
semantic_key: rdiscinf__markup
title: Markup (RDISCINF)
display_names:
- MARKUP
kind: flag
tables:
- ref: db2:rdiscinf
  column: MARKUP
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Markup (RDISCINF)

**Semantic key:** `rdiscinf__markup` · **Cột vật lý:** `MARKUP`

## Ý nghĩa nghiệp vụ

Cờ rule markup giá — tăng/giảm giá theo điều kiện thay vì chiết khấu trực tiếp.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `MARKUP` | bit | Cờ / trạng thái (markup) trên rule khuyến mãi / chiết khấu |
