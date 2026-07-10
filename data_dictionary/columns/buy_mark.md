---
semantic_key: buy_mark
title: buy mark
display_names:
- BUY_MARK
kind: measure
tables:
- ref: db2:pmcrdinf
  column: BUY_MARK
  type: numeric
- ref: db2:pmcrdiss
  column: BUY_MARK
  type: numeric
- ref: db2:pmcrdrcv
  column: BUY_MARK
  type: numeric
- ref: db2:pmcrdstk
  column: BUY_MARK
  type: numeric
- ref: db2:rdiscinf
  column: BUY_MARK
  type: numeric
- ref: db2:sku_def
  column: BUY_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_MARK'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# buy mark

**Semantic key:** `buy_mark` · **Cột vật lý:** `BUY_MARK`

## Ý nghĩa nghiệp vụ

Phát sinh mua/tích: BUY_MARK. Dùng trong Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |
| `db2:pmcrdiss` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |
| `db2:pmcrdrcv` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |
| `db2:pmcrdstk` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |
| `db2:rdiscinf` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |
| `db2:sku_def` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |
