---
semantic_key: strans__staff_id
title: Mã định danh (staff id) (STRANS)
display_names:
- STAFF_ID
kind: identifier
tables:
- ref: db1:strans
  column: STAFF_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã nhân viên
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (staff id) (STRANS)

**Semantic key:** `strans__staff_id` · **Cột vật lý:** `STAFF_ID`

## Ý nghĩa nghiệp vụ

Mã định danh (staff id) — dòng bán hàng POS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `STAFF_ID` | char | Mã nhân viên |

## Ghi chú thêm

- Mã nhân viên
