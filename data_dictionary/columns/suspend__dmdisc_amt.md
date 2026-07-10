---
semantic_key: suspend__dmdisc_amt
title: Số tiền / giá trị (SUSPEND)
display_names:
- DMDISC_AMT
kind: measure
tables:
- ref: db2:suspend
  column: DMDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnDMDISC_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (SUSPEND)

**Semantic key:** `suspend__dmdisc_amt` · **Cột vật lý:** `DMDISC_AMT`

## Ý nghĩa nghiệp vụ

Số tiền / giá trị — bill đang treo / chưa hoàn tất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:suspend` | `DMDISC_AMT` | numeric | Số tiềnDMDISC_AMT |

## Ghi chú thêm

- Số tiềnDMDISC_AMT
