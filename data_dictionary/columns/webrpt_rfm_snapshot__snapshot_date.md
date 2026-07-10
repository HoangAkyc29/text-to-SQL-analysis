---
semantic_key: webrpt_rfm_snapshot__snapshot_date
title: Ngày snapshot (WEBRPT_RFM_SNAPSHOT)
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
- column_semantic_registry
- business_prose
---

# Ngày snapshot (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__snapshot_date` · **Cột vật lý:** `snapshot_date`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `snapshot_date` | date | Ngày snapshot |

## Ghi chú thêm

- Ngày snapshot
