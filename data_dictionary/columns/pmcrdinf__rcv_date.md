---
semantic_key: pmcrdinf__rcv_date
title: pmcrdinf · rcv date
display_names:
- RCV_DATE
kind: date
tables:
- ref: db2:pmcrdinf
  column: RCV_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyRCV_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RCV_DATE
- 'db2:pmcrdinf.RCV_DATE: top=2022-01-24 00:00:00(4), 2025-01-18 00:00:00(4), 2018-02-06
  00:00:00(3), 2024-01-25 00:00:00(3), 2020-12-12 00:00:00(3)'
---

# pmcrdinf · rcv date

**Semantic key:** `pmcrdinf__rcv_date` · **Cột vật lý:** `RCV_DATE`

## Ý nghĩa nghiệp vụ

NgàyRCV_DATE

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `RCV_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

