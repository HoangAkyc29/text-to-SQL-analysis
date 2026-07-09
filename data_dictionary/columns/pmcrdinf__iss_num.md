---
semantic_key: pmcrdinf__iss_num
title: pmcrdinf · iss num
display_names:
- ISS_NUM
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: ISS_NUM
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột ISS_NUM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ISS_NUM
- 'db2:pmcrdinf.ISS_NUM: top=000008241704000025(6), 000008241704000024(6), 000008241709000023(5),
  000008241511000020(5), 000008241611000021(4)'
---

# pmcrdinf · iss num

**Semantic key:** `pmcrdinf__iss_num` · **Cột vật lý:** `ISS_NUM`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `ISS_NUM` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột ISS_NUM
