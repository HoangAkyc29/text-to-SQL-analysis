---
semantic_key: webrpt_rfm_snapshot__rfm_segment
title: webrpt rfm snapshot · rfm segment
display_names:
- rfm_segment
kind: text
tables:
- ref: db2:webrpt_rfm_snapshot
  column: rfm_segment
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- 'Phân khúc RFM: At Risk, Loyal, Others'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for rfm_segment
- 'db2:webrpt_rfm_snapshot.rfm_segment: top=Others(629), Loyal(226), Champions(116),
  At Risk(29)'
---

# webrpt rfm snapshot · rfm segment

**Semantic key:** `webrpt_rfm_snapshot__rfm_segment` · **Cột vật lý:** `rfm_segment`

## Ý nghĩa nghiệp vụ

Cột RFM_SEGMENT trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: top Others, Loyal, At Risk.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `rfm_segment` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.rfm_segment`
- Null rate trong sample: 0%
- Distinct ≈3; top: `Others`×15, `Loyal`×4, `At Risk`×1

## Ghi chú thêm

- Phân khúc RFM: At Risk, Loyal, Others
