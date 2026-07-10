---
semantic_key: mdadd_rate
title: Tỷ lệ phụ thu markdown (%) (MDADD_RATE)
display_names:
- MDADD_RATE
kind: measure
tables:
- ref: db1:strans
  column: MDADD_RATE
  type: numeric
- ref: db2:st_order
  column: MDADD_RATE
  type: numeric
- ref: db2:strans
  column: MDADD_RATE
  type: numeric
- ref: db2:strans_tmp
  column: MDADD_RATE
  type: numeric
- ref: db2:suspend
  column: MDADD_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu manual: MDADD_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ phụ thu markdown (%) (MDADD_RATE)

**Semantic key:** `mdadd_rate` · **Cột vật lý:** `MDADD_RATE`

## Ý nghĩa nghiệp vụ

Phụ thu manual: MDADD_RATE. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MDADD_RATE` | numeric | Phụ thu manual: MDADD_RATE |
| `db2:st_order` | `MDADD_RATE` | numeric | Phụ thu manual: MDADD_RATE |
| `db2:strans` | `MDADD_RATE` | numeric | Phụ thu manual: MDADD_RATE |
| `db2:strans_tmp` | `MDADD_RATE` | numeric | Phụ thu manual: MDADD_RATE |
| `db2:suspend` | `MDADD_RATE` | numeric | Phụ thu manual: MDADD_RATE |
