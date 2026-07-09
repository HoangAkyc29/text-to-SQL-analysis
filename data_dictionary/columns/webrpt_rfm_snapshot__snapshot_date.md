---
semantic_key: webrpt_rfm_snapshot__snapshot_date
title: webrpt rfm snapshot · snapshot date
display_names:
- snapshot_date
kind: date
tables:
- ref: db2:webrpt_rfm_snapshot
  column: snapshot_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày snapshot
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for snapshot_date
- 'db2:webrpt_rfm_snapshot.snapshot_date: top=2026-04-01(1000)'
---

# webrpt rfm snapshot · snapshot date

**Semantic key:** `webrpt_rfm_snapshot__snapshot_date` · **Cột vật lý:** `snapshot_date`

## Ý nghĩa nghiệp vụ

Cột SNAPSHOT_DATE trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: top 2026-04-01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `snapshot_date` | date | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.snapshot_date`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-01`×20

## Ghi chú thêm

- Ngày snapshot
