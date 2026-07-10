---
semantic_key: webrpt_rfm_snapshot__rfm_segment
title: Rfm Segment (WEBRPT_RFM_SNAPSHOT)
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
- column_semantic_registry
- business_prose
---

# Rfm Segment (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__rfm_segment` · **Cột vật lý:** `rfm_segment`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `rfm_segment` | varchar | Phân khúc RFM: At Risk, Loyal, Others |

## Ghi chú thêm

- Phân khúc RFM: At Risk, Loyal, Others
