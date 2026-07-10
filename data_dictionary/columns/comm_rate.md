---
semantic_key: comm_rate
title: Tỷ lệ hoa hồng (%) (COMM_RATE)
display_names:
- COMM_RATE
kind: measure
tables:
- ref: db1:strans
  column: COMM_RATE
  type: numeric
- ref: db2:customer
  column: COMM_RATE
  type: numeric
- ref: db2:st_order
  column: COMM_RATE
  type: decimal
- ref: db2:strans
  column: COMM_RATE
  type: numeric
- ref: db2:strans_tmp
  column: COMM_RATE
  type: numeric
- ref: db2:supplier
  column: COMM_RATE
  type: numeric
- ref: db2:suspend
  column: COMM_RATE
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệ hoa hồng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ hoa hồng (%) (COMM_RATE)

**Semantic key:** `comm_rate` · **Cột vật lý:** `COMM_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ hoa hồng. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER); Master / danh mục (CUSTOMER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `COMM_RATE` | numeric | Tỷ lệ hoa hồng |
| `db2:customer` | `COMM_RATE` | numeric | Tỷ lệ hoa hồng |
| `db2:st_order` | `COMM_RATE` | decimal | Tỷ lệ hoa hồng |
| `db2:strans` | `COMM_RATE` | numeric | Tỷ lệ hoa hồng |
| `db2:strans_tmp` | `COMM_RATE` | numeric | Tỷ lệ hoa hồng |
| `db2:supplier` | `COMM_RATE` | numeric | Tỷ lệ hoa hồng |
| `db2:suspend` | `COMM_RATE` | decimal | Tỷ lệ hoa hồng |
