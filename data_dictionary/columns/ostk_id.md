---
semantic_key: ostk_id
title: ostk id
display_names:
- OSTK_ID
kind: identifier
tables:
- ref: db1:strans
  column: OSTK_ID
  type: char
- ref: db2:st_order
  column: OSTK_ID
  type: char
- ref: db2:strans
  column: OSTK_ID
  type: char
- ref: db2:strans_tmp
  column: OSTK_ID
  type: char
- ref: db2:suspend
  column: OSTK_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Kho đích / kho đối ứng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# ostk id

**Semantic key:** `ostk_id` · **Cột vật lý:** `OSTK_ID`

## Ý nghĩa nghiệp vụ

Kho đích / kho đối ứng. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `OSTK_ID` | char | Kho đích / kho đối ứng |
| `db2:st_order` | `OSTK_ID` | char | Kho đích / kho đối ứng |
| `db2:strans` | `OSTK_ID` | char | Kho đích / kho đối ứng |
| `db2:strans_tmp` | `OSTK_ID` | char | Kho đích / kho đối ứng |
| `db2:suspend` | `OSTK_ID` | char | Kho đích / kho đối ứng |
