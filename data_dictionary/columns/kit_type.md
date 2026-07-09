---
semantic_key: kit_type
title: kit type
display_names:
- KIT_TYPE
kind: text
tables:
- ref: db2:strans
  column: KIT_TYPE
  type: char
- ref: db2:strans_tmp
  column: KIT_TYPE
  type: char
- ref: db2:suspend
  column: KIT_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột KIT_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:strans.KIT_TYPE: top=01(1)'
- 'db2:strans_tmp.KIT_TYPE: top=01(1)'
- 'db2:suspend.KIT_TYPE: top=01(3)'
---

# kit type

**Semantic key:** `kit_type` · **Cột vật lý:** `KIT_TYPE`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:strans` | `KIT_TYPE` | char | có dữ liệu |
| `db2:strans_tmp` | `KIT_TYPE` | char | có dữ liệu |
| `db2:suspend` | `KIT_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột KIT_TYPE
