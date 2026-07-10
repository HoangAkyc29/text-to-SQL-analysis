---
semantic_key: chg_value
title: chg value
display_names:
- CHG_VALUE
kind: measure
tables:
- ref: db2:pmcrdiss
  column: CHG_VALUE
  type: numeric
- ref: db2:rdiscinf
  column: CHG_VALUE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# chg value

**Semantic key:** `chg_value` · **Cột vật lý:** `CHG_VALUE`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (chg value) — dùng trong bảng PMCRDISS, rule khuyến mãi / chiết khấu.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdiss` | `CHG_VALUE` | numeric | Chỉ số đo lường (chg value) trên bảng pmcrdiss |
| `db2:rdiscinf` | `CHG_VALUE` | numeric | Chỉ số đo lường (chg value) trên rule khuyến mãi / chiết khấu |
