---
semantic_key: rdiscinf__dowmap
title: Dowmap (RDISCINF)
display_names:
- DOWMAP
kind: text
tables:
- ref: db2:rdiscinf
  column: DOWMAP
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Dowmap (RDISCINF)

**Semantic key:** `rdiscinf__dowmap` · **Cột vật lý:** `DOWMAP`

## Ý nghĩa nghiệp vụ

Bitmap ngày trong tuần áp dụng rule (Mon–Sun).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `DOWMAP` | char | Thuộc tính dowmap trên rule khuyến mãi / chiết khấu |
