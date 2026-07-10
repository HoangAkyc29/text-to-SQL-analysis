---
semantic_key: ccomm_rate
title: ccomm rate
display_names:
- CCOMM_RATE
kind: measure
tables:
- ref: db1:strans
  column: CCOMM_RATE
  type: numeric
- ref: db2:st_order
  column: CCOMM_RATE
  type: numeric
- ref: db2:strans
  column: CCOMM_RATE
  type: numeric
- ref: db2:strans_tmp
  column: CCOMM_RATE
  type: numeric
- ref: db2:suspend
  column: CCOMM_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng coupon: CCOMM_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# ccomm rate

**Semantic key:** `ccomm_rate` · **Cột vật lý:** `CCOMM_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ hoa hồng coupon (%) trên dòng / đơn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `CCOMM_RATE` | numeric | Hoa hồng coupon: CCOMM_RATE |
| `db2:st_order` | `CCOMM_RATE` | numeric | Hoa hồng coupon: CCOMM_RATE |
| `db2:strans` | `CCOMM_RATE` | numeric | Hoa hồng coupon: CCOMM_RATE |
| `db2:strans_tmp` | `CCOMM_RATE` | numeric | Hoa hồng coupon: CCOMM_RATE |
| `db2:suspend` | `CCOMM_RATE` | numeric | Hoa hồng coupon: CCOMM_RATE |

## Ghi chú thêm

- Hoa hồng coupon: CCOMM_RATE
