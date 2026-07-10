---
semantic_key: tdadd_amt
title: Số tiền phụ thu thêm (trade add-on) (TDADD_AMT)
display_names:
- TDADD_AMT
kind: measure
tables:
- ref: db1:strans
  column: TDADD_AMT
  type: numeric
- ref: db2:st_order
  column: TDADD_AMT
  type: numeric
- ref: db2:strans
  column: TDADD_AMT
  type: numeric
- ref: db2:strans_tmp
  column: TDADD_AMT
  type: numeric
- ref: db2:suspend
  column: TDADD_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu transaction: TDADD_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền phụ thu thêm (trade add-on) (TDADD_AMT)

**Semantic key:** `tdadd_amt` · **Cột vật lý:** `TDADD_AMT`

## Ý nghĩa nghiệp vụ

Phụ thu transaction: TDADD_AMT. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TDADD_AMT` | numeric | Phụ thu transaction: TDADD_AMT |
| `db2:st_order` | `TDADD_AMT` | numeric | Phụ thu transaction: TDADD_AMT |
| `db2:strans` | `TDADD_AMT` | numeric | Phụ thu transaction: TDADD_AMT |
| `db2:strans_tmp` | `TDADD_AMT` | numeric | Phụ thu transaction: TDADD_AMT |
| `db2:suspend` | `TDADD_AMT` | numeric | Phụ thu transaction: TDADD_AMT |
