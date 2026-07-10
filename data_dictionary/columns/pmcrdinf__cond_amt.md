---
semantic_key: pmcrdinf__cond_amt
title: Số tiền / giá trị (PMCRDINF)
display_names:
- COND_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: COND_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnCOND_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (PMCRDINF)

**Semantic key:** `pmcrdinf__cond_amt` · **Cột vật lý:** `COND_AMT`

## Ý nghĩa nghiệp vụ

Ngưỡng giá trị bill tối thiểu để voucher PM có hiệu lực (điều kiện sử dụng).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `COND_AMT` | numeric | Số tiềnCOND_AMT |

## Ghi chú thêm

- Số tiềnCOND_AMT
