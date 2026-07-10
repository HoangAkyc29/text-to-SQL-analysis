---
semantic_key: tcomm_amt
title: tcomm amt
display_names:
- TCOMM_AMT
kind: measure
tables:
- ref: db1:strans
  column: TCOMM_AMT
  type: numeric
- ref: db2:st_order
  column: TCOMM_AMT
  type: numeric
- ref: db2:strans
  column: TCOMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: TCOMM_AMT
  type: numeric
- ref: db2:suspend
  column: TCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng transaction: TCOMM_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# tcomm amt

**Semantic key:** `tcomm_amt` · **Cột vật lý:** `TCOMM_AMT`

## Ý nghĩa nghiệp vụ

Tiền hoa hồng thương mại trên dòng / đơn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TCOMM_AMT` | numeric | Hoa hồng transaction: TCOMM_AMT |
| `db2:st_order` | `TCOMM_AMT` | numeric | Hoa hồng transaction: TCOMM_AMT |
| `db2:strans` | `TCOMM_AMT` | numeric | Hoa hồng transaction: TCOMM_AMT |
| `db2:strans_tmp` | `TCOMM_AMT` | numeric | Hoa hồng transaction: TCOMM_AMT |
| `db2:suspend` | `TCOMM_AMT` | numeric | Hoa hồng transaction: TCOMM_AMT |

## Ghi chú thêm

- Hoa hồng transaction: TCOMM_AMT
