---
semantic_key: rdiscinf__sold_amt
title: Số tiền / giá trị (RDISCINF)
display_names:
- SOLD_AMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: SOLD_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnSOLD_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (RDISCINF)

**Semantic key:** `rdiscinf__sold_amt` · **Cột vật lý:** `SOLD_AMT`

## Ý nghĩa nghiệp vụ

Ngưỡng doanh số / tiền hàng đã bán để rule KM kích hoạt — hay dùng cho min bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `SOLD_AMT` | numeric | Số tiềnSOLD_AMT |

## Ghi chú thêm

- Số tiềnSOLD_AMT
