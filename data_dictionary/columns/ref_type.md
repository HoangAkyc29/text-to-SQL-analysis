---
semantic_key: ref_type
title: ref type
display_names:
- REF_TYPE
kind: text
tables:
- ref: db1:transhdr_arc
  column: REF_TYPE
  type: char
- ref: db2:transhdr
  column: REF_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột REF_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.REF_TYPE: top=01(16)'
- 'db2:transhdr.REF_TYPE: top=01(11)'
---

# ref type

**Semantic key:** `ref_type` · **Cột vật lý:** `REF_TYPE`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `REF_TYPE` | char | có dữ liệu |
| `db2:transhdr` | `REF_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột REF_TYPE
