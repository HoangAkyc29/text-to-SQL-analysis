---
semantic_key: strans__staff_id
title: strans · staff id
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STAFF_ID
- 'db1:strans.STAFF_ID: top=465346(1)'
---

# strans · staff id

**Semantic key:** `strans__staff_id` · **Cột vật lý:** `STAFF_ID`

## Ý nghĩa nghiệp vụ

Mã nhân viên

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `STAFF_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

