---
semantic_key: rdiscinf__sold_cnt
title: Sold Cnt (RDISCINF)
display_names:
- SOLD_CNT
kind: measure
tables:
- ref: db2:rdiscinf
  column: SOLD_CNT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Sold Cnt (RDISCINF)

**Semantic key:** `rdiscinf__sold_cnt` · **Cột vật lý:** `SOLD_CNT`

## Ý nghĩa nghiệp vụ

Ngưỡng số lần giao dịch / số bill để rule KM kích hoạt.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `SOLD_CNT` | numeric | Chỉ số đo lường (sold cnt) trên rule khuyến mãi / chiết khấu |
