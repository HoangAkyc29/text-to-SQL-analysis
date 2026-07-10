---
semantic_key: supplier__supp_code
title: Mã nhà cung cấp hiển thị (SUPPLIER)
display_names:
- SUPP_CODE
kind: code
tables:
- ref: db2:supplier
  column: SUPP_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã NCC hiển thị
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã nhà cung cấp hiển thị (SUPPLIER)

**Semantic key:** `supplier__supp_code` · **Cột vật lý:** `SUPP_CODE`

## Ý nghĩa nghiệp vụ

Mã hiển thị / mã tra cứu nhà cung cấp — khác SUPP_ID nội bộ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `SUPP_CODE` | varchar | Mã NCC hiển thị |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã NCC hiển thị
