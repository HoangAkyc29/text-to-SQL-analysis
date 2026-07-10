---
semantic_key: fr_date
title: fr date
display_names:
- FR_DATE
kind: date
tables:
- ref: db2:inv_iss
  column: FR_DATE
  type: datetime
- ref: db2:rdiscinf
  column: FR_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyFR_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# fr date

**Semantic key:** `fr_date` · **Cột vật lý:** `FR_DATE`

## Ý nghĩa nghiệp vụ

Ngày bắt đầu hiệu lực (from date) — rule KM, giá, …

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `FR_DATE` | datetime | NgàyFR_DATE |
| `db2:rdiscinf` | `FR_DATE` | datetime | NgàyFR_DATE |

## Ghi chú thêm

- NgàyFR_DATE
