---
semantic_key: rdiscinf__gift
title: Gift (RDISCINF)
display_names:
- GIFT
kind: flag
tables:
- ref: db2:rdiscinf
  column: GIFT
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Gift (RDISCINF)

**Semantic key:** `rdiscinf__gift` · **Cột vật lý:** `GIFT`

## Ý nghĩa nghiệp vụ

Cờ đánh dấu rule quà tặng — khi bật, KM trả quà thay vì (hoặc kèm) giảm giá tiền.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `GIFT` | bit | Cờ / trạng thái (gift) trên rule khuyến mãi / chiết khấu |
