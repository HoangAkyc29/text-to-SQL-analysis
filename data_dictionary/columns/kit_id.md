---
semantic_key: kit_id
title: kit id
display_names:
- KIT_ID
kind: identifier
tables:
- ref: db2:strans
  column: KIT_ID
  type: char
- ref: db2:strans_tmp
  column: KIT_ID
  type: char
- ref: db2:suspend
  column: KIT_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã kit
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:strans.KIT_ID: top=280001000268(1)'
- 'db2:strans_tmp.KIT_ID: top=280001000147(1)'
- 'db2:suspend.KIT_ID: top=280001000186(1), 280001000135(1), 280001000147(1)'
---

# kit id

**Semantic key:** `kit_id` · **Cột vật lý:** `KIT_ID`

## Ý nghĩa nghiệp vụ

Mã kit

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:strans` | `KIT_ID` | char | có dữ liệu |
| `db2:strans_tmp` | `KIT_ID` | char | có dữ liệu |
| `db2:suspend` | `KIT_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

