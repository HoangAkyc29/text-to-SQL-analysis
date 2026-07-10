---
semantic_key: webrpt_rfm_snapshot__frequency
title: Frequency (WEBRPT_RFM_SNAPSHOT)
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
- column_semantic_registry
- business_prose
---

# Frequency (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__frequency` · **Cột vật lý:** `frequency`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `frequency` | int | Tần suất mua |

## Ghi chú thêm

- Tần suất mua
