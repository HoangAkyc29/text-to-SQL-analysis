---
semantic_key: suspend__dtdisc_amt
title: Số tiền / giá trị (SUSPEND)
display_names:
- DTDISC_AMT
kind: measure
tables:
- ref: db2:suspend
  column: DTDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnDTDISC_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (SUSPEND)

**Semantic key:** `suspend__dtdisc_amt` · **Cột vật lý:** `DTDISC_AMT`

## Ý nghĩa nghiệp vụ

Số tiền / giá trị — bill đang treo / chưa hoàn tất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:suspend` | `DTDISC_AMT` | numeric | Số tiềnDTDISC_AMT |

## Ghi chú thêm

- Số tiềnDTDISC_AMT
