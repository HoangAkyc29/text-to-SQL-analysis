---
semantic_key: st_order__gcomm_amt
title: Số tiền / giá trị (ST_ORDER)
display_names:
- GCOMM_AMT
kind: measure
tables:
- ref: db2:st_order
  column: GCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng gift: GCOMM_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (ST_ORDER)

**Semantic key:** `st_order__gcomm_amt` · **Cột vật lý:** `GCOMM_AMT`

## Ý nghĩa nghiệp vụ

Tiền hoa hồng / chi phí giao hàng trên đơn ST_ORDER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `GCOMM_AMT` | numeric | Hoa hồng gift: GCOMM_AMT |

## Ghi chú thêm

- Hoa hồng gift: GCOMM_AMT
