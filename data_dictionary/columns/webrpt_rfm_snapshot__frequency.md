---
semantic_key: webrpt_rfm_snapshot__frequency
title: webrpt rfm snapshot · frequency
display_names:
- frequency
kind: measure
tables:
- ref: db2:webrpt_rfm_snapshot
  column: frequency
  type: int
join_with: []
related_semantic_keys: []
facts:
- Tần suất mua
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for frequency
- 'db2:webrpt_rfm_snapshot.frequency: min=1.0 max=51.0'
---

# webrpt rfm snapshot · frequency

**Semantic key:** `webrpt_rfm_snapshot__frequency` · **Cột vật lý:** `frequency`

## Ý nghĩa nghiệp vụ

Cột FREQUENCY trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: 1.0…10.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `frequency` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.frequency`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 10.0
- Ví dụ: 1, 2, 1, 1, 1

## Ghi chú thêm

- Tần suất mua
