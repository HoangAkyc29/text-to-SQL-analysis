---
semantic_key: buy_amt
title: buy amt
display_names:
- BUY_AMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: BUY_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# buy amt

**Semantic key:** `buy_amt` · **Cột vật lý:** `BUY_AMT`

## Ý nghĩa nghiệp vụ

Ngưỡng giá trị mua / min bill trong rule khuyến mãi RDISCINF — khác BUY_AMT trên CRD_INFO (lifetime loyalty).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `BUY_AMT` | numeric | Phát sinh mua/tích: BUY_AMT |

## Ghi chú thêm

- Phát sinh mua/tích: BUY_AMT
