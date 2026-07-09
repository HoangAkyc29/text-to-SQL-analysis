---
semantic_key: webrpt_rfm_snapshot__recency_days
title: webrpt rfm snapshot · recency days
display_names:
- recency_days
kind: measure
tables:
- ref: db2:webrpt_rfm_snapshot
  column: recency_days
  type: int
join_with: []
related_semantic_keys: []
facts:
- Số ngày từ lần mua gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for recency_days
- 'db2:webrpt_rfm_snapshot.recency_days: min=0.0 max=89.0'
---

# webrpt rfm snapshot · recency days

**Semantic key:** `webrpt_rfm_snapshot__recency_days` · **Cột vật lý:** `recency_days`

## Ý nghĩa nghiệp vụ

Cột RECENCY_DAYS trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: 2.0…85.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `recency_days` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.recency_days`
- Null rate trong sample: 0%
- Numeric range: 2.0 … 85.0
- Ví dụ: 14, 64, 23, 26, 66

## Ghi chú thêm

- Số ngày từ lần mua gần nhất
