---
semantic_key: disc_amt
title: Tiền chiết khấu (DISC_AMT)
display_names:
- DISC_AMT
kind: measure
tables:
- ref: db2:custhist
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdinf
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdiss
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdrcv
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdstk
  column: DISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnDISC_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tiền chiết khấu (DISC_AMT)

**Semantic key:** `disc_amt` · **Cột vật lý:** `DISC_AMT`

## Ý nghĩa nghiệp vụ

Số tiền chiết khấu trên dòng/chứng từ — khác CDISC (coupon) và MDISC (khuyến mãi).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:custhist` | `DISC_AMT` | numeric | Số tiềnDISC_AMT |
| `db2:pmcrdinf` | `DISC_AMT` | numeric | Số tiềnDISC_AMT |
| `db2:pmcrdiss` | `DISC_AMT` | numeric | Số tiềnDISC_AMT |
| `db2:pmcrdrcv` | `DISC_AMT` | numeric | Số tiềnDISC_AMT |
| `db2:pmcrdstk` | `DISC_AMT` | numeric | Số tiềnDISC_AMT |

## Ghi chú thêm

- Số tiềnDISC_AMT
