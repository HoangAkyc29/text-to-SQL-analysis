---
semantic_key: rdiscinf__chg_type
title: Chg Type (RDISCINF)
display_names:
- CHG_TYPE
kind: text
tables:
- ref: db2:rdiscinf
  column: CHG_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Chg Type (RDISCINF)

**Semantic key:** `rdiscinf__chg_type` · **Cột vật lý:** `CHG_TYPE`

## Ý nghĩa nghiệp vụ

Kiểu thay đổi giá trị khi KM kích hoạt (%, tiền, quà, điểm, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CHG_TYPE` | char | Thuộc tính chg type trên rule khuyến mãi / chiết khấu |
