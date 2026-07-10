---
semantic_key: rdiscinf__sold_qty
title: Số lượng (RDISCINF)
display_names:
- SOLD_QTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: SOLD_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngSOLD_QTY
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (RDISCINF)

**Semantic key:** `rdiscinf__sold_qty` · **Cột vật lý:** `SOLD_QTY`

## Ý nghĩa nghiệp vụ

Ngưỡng số lượng đã bán / cần mua để rule KM kích hoạt.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `SOLD_QTY` | numeric | Số lượngSOLD_QTY |

## Ghi chú thêm

- Số lượngSOLD_QTY
