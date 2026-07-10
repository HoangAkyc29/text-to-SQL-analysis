---
semantic_key: mdadd_amt
title: Số tiền phụ thu markdown add-on (MDADD_AMT)
display_names:
- MDADD_AMT
kind: measure
tables:
- ref: db1:strans
  column: MDADD_AMT
  type: numeric
- ref: db2:st_order
  column: MDADD_AMT
  type: numeric
- ref: db2:strans
  column: MDADD_AMT
  type: numeric
- ref: db2:strans_tmp
  column: MDADD_AMT
  type: numeric
- ref: db2:suspend
  column: MDADD_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu manual: MDADD_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền phụ thu markdown add-on (MDADD_AMT)

**Semantic key:** `mdadd_amt` · **Cột vật lý:** `MDADD_AMT`

## Ý nghĩa nghiệp vụ

Phụ thu manual: MDADD_AMT. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MDADD_AMT` | numeric | Phụ thu manual: MDADD_AMT |
| `db2:st_order` | `MDADD_AMT` | numeric | Phụ thu manual: MDADD_AMT |
| `db2:strans` | `MDADD_AMT` | numeric | Phụ thu manual: MDADD_AMT |
| `db2:strans_tmp` | `MDADD_AMT` | numeric | Phụ thu manual: MDADD_AMT |
| `db2:suspend` | `MDADD_AMT` | numeric | Phụ thu manual: MDADD_AMT |
