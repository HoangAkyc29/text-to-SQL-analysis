---
semantic_key: gcomm_sqty
title: gcomm sqty
display_names:
- GCOMM_SQTY
kind: measure
tables:
- ref: db1:strans
  column: GCOMM_SQTY
  type: numeric
- ref: db2:st_order
  column: GCOMM_SQTY
  type: numeric
- ref: db2:strans
  column: GCOMM_SQTY
  type: numeric
- ref: db2:strans_tmp
  column: GCOMM_SQTY
  type: numeric
- ref: db2:suspend
  column: GCOMM_SQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng gift: GCOMM_SQTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# gcomm sqty

**Semantic key:** `gcomm_sqty` · **Cột vật lý:** `GCOMM_SQTY`

## Ý nghĩa nghiệp vụ

Hoa hồng gift: GCOMM_SQTY. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `GCOMM_SQTY` | numeric | Hoa hồng gift: GCOMM_SQTY |
| `db2:st_order` | `GCOMM_SQTY` | numeric | Hoa hồng gift: GCOMM_SQTY |
| `db2:strans` | `GCOMM_SQTY` | numeric | Hoa hồng gift: GCOMM_SQTY |
| `db2:strans_tmp` | `GCOMM_SQTY` | numeric | Hoa hồng gift: GCOMM_SQTY |
| `db2:suspend` | `GCOMM_SQTY` | numeric | Hoa hồng gift: GCOMM_SQTY |
