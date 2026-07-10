---
semantic_key: rdiscinf__cardincl
title: Cardincl (RDISCINF)
display_names:
- CARDINCL
kind: flag
tables:
- ref: db2:rdiscinf
  column: CARDINCL
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cardincl (RDISCINF)

**Semantic key:** `rdiscinf__cardincl` · **Cột vật lý:** `CARDINCL`

## Ý nghĩa nghiệp vụ

Cờ chỉ áp dụng cho loại thẻ trong danh sách include.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CARDINCL` | bit | Cờ / trạng thái (cardincl) trên rule khuyến mãi / chiết khấu |
