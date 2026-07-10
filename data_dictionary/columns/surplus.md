---
semantic_key: surplus
title: Số lượng / giá trị thặng dư (SURPLUS)
display_names:
- SURPLUS
kind: measure
tables:
- ref: db1:strans
  column: SURPLUS
  type: numeric
- ref: db1:transhdr_arc
  column: SURPLUS
  type: numeric
- ref: db2:st_order
  column: SURPLUS
  type: decimal
- ref: db2:strans
  column: SURPLUS
  type: numeric
- ref: db2:strans_tmp
  column: SURPLUS
  type: numeric
- ref: db2:suspend
  column: SURPLUS
  type: numeric
- ref: db2:transhdr
  column: SURPLUS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Phụ phí / surplus
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng / giá trị thặng dư (SURPLUS)

**Semantic key:** `surplus` · **Cột vật lý:** `SURPLUS`

## Ý nghĩa nghiệp vụ

Phụ phí / surplus. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `SURPLUS` | numeric | Phụ phí / surplus |
| `db1:transhdr_arc` | `SURPLUS` | numeric | Phụ phí / surplus |
| `db2:st_order` | `SURPLUS` | decimal | Phụ phí / surplus |
| `db2:strans` | `SURPLUS` | numeric | Phụ phí / surplus |
| `db2:strans_tmp` | `SURPLUS` | numeric | Phụ phí / surplus |
| `db2:suspend` | `SURPLUS` | numeric | Phụ phí / surplus |
| `db2:transhdr` | `SURPLUS` | numeric | Phụ phí / surplus |
