---
semantic_key: cdisc_rate
title: Tỷ lệ chiết khấu coupon (%) (CDISC_RATE)
display_names:
- CDISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: CDISC_RATE
  type: numeric
- ref: db2:st_order
  column: CDISC_RATE
  type: decimal
- ref: db2:strans
  column: CDISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: CDISC_RATE
  type: numeric
- ref: db2:suspend
  column: CDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu coupon: CDISC_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ chiết khấu coupon (%) (CDISC_RATE)

**Semantic key:** `cdisc_rate` · **Cột vật lý:** `CDISC_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ chiết khấu coupon (%) trên dòng bán STRANS / đơn KM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `CDISC_RATE` | numeric | Chiết khấu coupon: CDISC_RATE |
| `db2:st_order` | `CDISC_RATE` | decimal | Chiết khấu coupon: CDISC_RATE |
| `db2:strans` | `CDISC_RATE` | numeric | Chiết khấu coupon: CDISC_RATE |
| `db2:strans_tmp` | `CDISC_RATE` | numeric | Chiết khấu coupon: CDISC_RATE |
| `db2:suspend` | `CDISC_RATE` | numeric | Chiết khấu coupon: CDISC_RATE |

## Ghi chú thêm

- Chiết khấu coupon: CDISC_RATE
