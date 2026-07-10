---
semantic_key: tdadd_rate
title: Tỷ lệ phụ thu thêm (%) (TDADD_RATE)
display_names:
- TDADD_RATE
kind: measure
tables:
- ref: db1:strans
  column: TDADD_RATE
  type: numeric
- ref: db2:st_order
  column: TDADD_RATE
  type: numeric
- ref: db2:strans
  column: TDADD_RATE
  type: numeric
- ref: db2:strans_tmp
  column: TDADD_RATE
  type: numeric
- ref: db2:suspend
  column: TDADD_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu transaction: TDADD_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ phụ thu thêm (%) (TDADD_RATE)

**Semantic key:** `tdadd_rate` · **Cột vật lý:** `TDADD_RATE`

## Ý nghĩa nghiệp vụ

Phụ thu transaction: TDADD_RATE. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TDADD_RATE` | numeric | Phụ thu transaction: TDADD_RATE |
| `db2:st_order` | `TDADD_RATE` | numeric | Phụ thu transaction: TDADD_RATE |
| `db2:strans` | `TDADD_RATE` | numeric | Phụ thu transaction: TDADD_RATE |
| `db2:strans_tmp` | `TDADD_RATE` | numeric | Phụ thu transaction: TDADD_RATE |
| `db2:suspend` | `TDADD_RATE` | numeric | Phụ thu transaction: TDADD_RATE |
