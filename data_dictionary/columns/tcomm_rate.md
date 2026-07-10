---
semantic_key: tcomm_rate
title: tcomm rate
display_names:
- TCOMM_RATE
kind: measure
tables:
- ref: db1:strans
  column: TCOMM_RATE
  type: numeric
- ref: db2:st_order
  column: TCOMM_RATE
  type: numeric
- ref: db2:strans
  column: TCOMM_RATE
  type: numeric
- ref: db2:strans_tmp
  column: TCOMM_RATE
  type: numeric
- ref: db2:suspend
  column: TCOMM_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng transaction: TCOMM_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# tcomm rate

**Semantic key:** `tcomm_rate` · **Cột vật lý:** `TCOMM_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ hoa hồng thương mại (%) trên dòng / đơn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TCOMM_RATE` | numeric | Hoa hồng transaction: TCOMM_RATE |
| `db2:st_order` | `TCOMM_RATE` | numeric | Hoa hồng transaction: TCOMM_RATE |
| `db2:strans` | `TCOMM_RATE` | numeric | Hoa hồng transaction: TCOMM_RATE |
| `db2:strans_tmp` | `TCOMM_RATE` | numeric | Hoa hồng transaction: TCOMM_RATE |
| `db2:suspend` | `TCOMM_RATE` | numeric | Hoa hồng transaction: TCOMM_RATE |

## Ghi chú thêm

- Hoa hồng transaction: TCOMM_RATE
