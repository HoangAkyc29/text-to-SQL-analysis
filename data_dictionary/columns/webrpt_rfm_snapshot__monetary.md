---
semantic_key: webrpt_rfm_snapshot__monetary
title: Monetary (WEBRPT_RFM_SNAPSHOT)
display_names:
- monetary
kind: measure
tables:
- ref: db2:webrpt_rfm_snapshot
  column: monetary
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chi tiêu
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Monetary (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__monetary` · **Cột vật lý:** `monetary`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `monetary` | decimal | Tổng chi tiêu |

## Ghi chú thêm

- Tổng chi tiêu
