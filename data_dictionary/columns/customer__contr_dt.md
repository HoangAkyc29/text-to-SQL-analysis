---
semantic_key: customer__contr_dt
title: customer · contr dt
display_names:
- CONTR_DT
kind: date
tables:
- ref: db2:customer
  column: CONTR_DT
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Cột CONTR_DT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CONTR_DT
- 'db2:customer.CONTR_DT: top=1900-01-01 00:00:00(350)'
---

# customer · contr dt

**Semantic key:** `customer__contr_dt` · **Cột vật lý:** `CONTR_DT`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CONTR_DT` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột CONTR_DT
