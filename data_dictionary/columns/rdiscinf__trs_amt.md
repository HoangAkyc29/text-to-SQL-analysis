---
semantic_key: rdiscinf__trs_amt
title: Số tiền / giá trị (RDISCINF)
display_names:
- TRS_AMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: TRS_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnTRS_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (RDISCINF)

**Semantic key:** `rdiscinf__trs_amt` · **Cột vật lý:** `TRS_AMT`

## Ý nghĩa nghiệp vụ

Ngưỡng tiền giao dịch trong rule — thường so với tổng bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `TRS_AMT` | numeric | Số tiềnTRS_AMT |

## Ghi chú thêm

- Số tiềnTRS_AMT
