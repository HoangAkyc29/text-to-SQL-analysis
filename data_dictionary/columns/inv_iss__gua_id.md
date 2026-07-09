---
semantic_key: inv_iss__gua_id
title: inv iss · gua id
display_names:
- Gua_ID
kind: identifier
tables:
- ref: db2:inv_iss
  column: Gua_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột Gua_ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for Gua_ID
- 'db2:inv_iss.Gua_ID: top=1057110(1), 1076462(1), 1055688(1), 1123283(1)'
---

# inv iss · gua id

**Semantic key:** `inv_iss__gua_id` · **Cột vật lý:** `Gua_ID`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `Gua_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột Gua_ID
