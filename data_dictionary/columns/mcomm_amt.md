---
semantic_key: mcomm_amt
title: mcomm amt
display_names:
- MCOMM_AMT
kind: measure
tables:
- ref: db1:strans
  column: MCOMM_AMT
  type: numeric
- ref: db2:st_order
  column: MCOMM_AMT
  type: numeric
- ref: db2:strans
  column: MCOMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: MCOMM_AMT
  type: numeric
- ref: db2:suspend
  column: MCOMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng manual: MCOMM_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# mcomm amt

**Semantic key:** `mcomm_amt` · **Cột vật lý:** `MCOMM_AMT`

## Ý nghĩa nghiệp vụ

Tiền hoa hồng khuyến mãi trên dòng / đơn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MCOMM_AMT` | numeric | Hoa hồng manual: MCOMM_AMT |
| `db2:st_order` | `MCOMM_AMT` | numeric | Hoa hồng manual: MCOMM_AMT |
| `db2:strans` | `MCOMM_AMT` | numeric | Hoa hồng manual: MCOMM_AMT |
| `db2:strans_tmp` | `MCOMM_AMT` | numeric | Hoa hồng manual: MCOMM_AMT |
| `db2:suspend` | `MCOMM_AMT` | numeric | Hoa hồng manual: MCOMM_AMT |

## Ghi chú thêm

- Hoa hồng manual: MCOMM_AMT
