---
semantic_key: base_unit
title: Đơn vị cơ sở quy đổi (BASE_UNIT)
display_names:
- BASE_UNIT
kind: text
tables:
- ref: db1:strans
  column: BASE_UNIT
  type: char
- ref: db2:asso_inf
  column: BASE_UNIT
  type: char
- ref: db2:hisrtpr
  column: BASE_UNIT
  type: char
- ref: db2:hissppr
  column: BASE_UNIT
  type: char
- ref: db2:st_order
  column: BASE_UNIT
  type: char
- ref: db2:strans
  column: BASE_UNIT
  type: char
- ref: db2:strans_tmp
  column: BASE_UNIT
  type: char
- ref: db2:suspend
  column: BASE_UNIT
  type: char
join_with: []
related_semantic_keys: []
facts:
- Đơn vị cơ sở
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Đơn vị cơ sở quy đổi (BASE_UNIT)

**Semantic key:** `base_unit` · **Cột vật lý:** `BASE_UNIT`

## Ý nghĩa nghiệp vụ

Đơn vị cơ sở. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:asso_inf` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:hisrtpr` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:hissppr` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:st_order` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:strans` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:strans_tmp` | `BASE_UNIT` | char | Đơn vị cơ sở |
| `db2:suspend` | `BASE_UNIT` | char | Đơn vị cơ sở |
