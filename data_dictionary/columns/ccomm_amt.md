---
semantic_key: ccomm_amt
title: ccomm amt
display_names:
- CCOMM_AMT
kind: measure
tables:
- ref: db1:strans
  column: CCOMM_AMT
  type: numeric
- ref: db2:st_order
  column: CCOMM_AMT
  type: numeric
- ref: db2:strans
  column: CCOMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: CCOMM_AMT
  type: numeric
- ref: db2:suspend
  column: CCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng coupon: CCOMM_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# ccomm amt

**Semantic key:** `ccomm_amt` · **Cột vật lý:** `CCOMM_AMT`

## Ý nghĩa nghiệp vụ

Tiền hoa hồng coupon trên dòng bán / đơn hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `CCOMM_AMT` | numeric | Hoa hồng coupon: CCOMM_AMT |
| `db2:st_order` | `CCOMM_AMT` | numeric | Hoa hồng coupon: CCOMM_AMT |
| `db2:strans` | `CCOMM_AMT` | numeric | Hoa hồng coupon: CCOMM_AMT |
| `db2:strans_tmp` | `CCOMM_AMT` | numeric | Hoa hồng coupon: CCOMM_AMT |
| `db2:suspend` | `CCOMM_AMT` | numeric | Hoa hồng coupon: CCOMM_AMT |

## Ghi chú thêm

- Hoa hồng coupon: CCOMM_AMT
