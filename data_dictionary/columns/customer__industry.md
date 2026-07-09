---
semantic_key: customer__industry
title: customer · industry
display_names:
- INDUSTRY
kind: text
tables:
- ref: db2:customer
  column: INDUSTRY
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột INDUSTRY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for INDUSTRY
- 'db2:customer.INDUSTRY: top=N1(425)'
---

# customer · industry

**Semantic key:** `customer__industry` · **Cột vật lý:** `INDUSTRY`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `INDUSTRY` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột INDUSTRY
