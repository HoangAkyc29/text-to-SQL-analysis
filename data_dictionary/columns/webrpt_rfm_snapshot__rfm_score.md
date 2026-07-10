---
semantic_key: webrpt_rfm_snapshot__rfm_score
title: Rfm Score (WEBRPT_RFM_SNAPSHOT)
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
- column_semantic_registry
- business_prose
---

# Rfm Score (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__rfm_score` · **Cột vật lý:** `rfm_score`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `rfm_score` | tinyint | Điểm RFM |

## Ghi chú thêm

- Điểm RFM
