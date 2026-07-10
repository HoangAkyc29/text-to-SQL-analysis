---
semantic_key: webrpt_rfm_snapshot__card_type
title: Card Type (WEBRPT_RFM_SNAPSHOT)
display_names:
- card_type
kind: text
tables:
- ref: db2:webrpt_rfm_snapshot
  column: card_type
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Loại thẻ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Card Type (WEBRPT_RFM_SNAPSHOT)

**Semantic key:** `webrpt_rfm_snapshot__card_type` · **Cột vật lý:** `card_type`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `card_type` | varchar | Loại thẻ |

## Ghi chú thêm

- Loại thẻ
