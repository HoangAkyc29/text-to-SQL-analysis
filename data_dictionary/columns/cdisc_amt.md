---
semantic_key: cdisc_amt
title: Chiết khấu coupon (CDISC_AMT)
display_names:
- CDISC_AMT
kind: measure
tables:
- ref: db1:strans
  column: CDISC_AMT
  type: numeric
- ref: db2:st_order
  column: CDISC_AMT
  type: numeric
- ref: db2:strans
  column: CDISC_AMT
  type: numeric
- ref: db2:strans_tmp
  column: CDISC_AMT
  type: numeric
- ref: db2:suspend
  column: CDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu coupon: CDISC_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Chiết khấu coupon (CDISC_AMT)

**Semantic key:** `cdisc_amt` · **Cột vật lý:** `CDISC_AMT`

## Ý nghĩa nghiệp vụ

Số tiền chiết khấu từ coupon (CDISC) trên dòng bán hoặc đơn hàng — khác DISCOUNT thông thường và MDISC khuyến mãi.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `CDISC_AMT` | numeric | Chiết khấu coupon: CDISC_AMT |
| `db2:st_order` | `CDISC_AMT` | numeric | Chiết khấu coupon: CDISC_AMT |
| `db2:strans` | `CDISC_AMT` | numeric | Chiết khấu coupon: CDISC_AMT |
| `db2:strans_tmp` | `CDISC_AMT` | numeric | Chiết khấu coupon: CDISC_AMT |
| `db2:suspend` | `CDISC_AMT` | numeric | Chiết khấu coupon: CDISC_AMT |

## Ghi chú thêm

- Chiết khấu coupon: CDISC_AMT
