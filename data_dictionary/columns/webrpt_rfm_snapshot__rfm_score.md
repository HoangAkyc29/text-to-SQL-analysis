---
semantic_key: webrpt_rfm_snapshot__rfm_score
title: webrpt rfm snapshot · rfm score
display_names:
- rfm_score
kind: text
tables:
- ref: db2:webrpt_rfm_snapshot
  column: rfm_score
  type: tinyint
join_with: []
related_semantic_keys: []
facts:
- Điểm RFM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for rfm_score
- 'db2:webrpt_rfm_snapshot.rfm_score: min=2.0 max=5.0'
---

# webrpt rfm snapshot · rfm score

**Semantic key:** `webrpt_rfm_snapshot__rfm_score` · **Cột vật lý:** `rfm_score`

## Ý nghĩa nghiệp vụ

Cột RFM_SCORE trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: 2.0…4.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `rfm_score` | tinyint | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.rfm_score`
- Null rate trong sample: 0%
- Numeric range: 2.0 … 4.0
- Ví dụ: 3, 2, 3, 3, 2

## Ghi chú thêm

- Điểm RFM
