---
semantic_key: webrpt_rfm_snapshot__recency_days
title: Recency Days (WEBRPT_RFM_SNAPSHOT)
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
- column_semantic_registry
- business_prose
---

# Recency Days (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__recency_days` · **Cột vật lý:** `recency_days`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `recency_days` | int | Số ngày từ lần mua gần nhất |

## Ghi chú thêm

- Số ngày từ lần mua gần nhất
