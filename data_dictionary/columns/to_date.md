---
semantic_key: to_date
title: to date
display_names:
- TO_DATE
kind: date
tables:
- ref: db2:inv_iss
  column: TO_DATE
  type: datetime
- ref: db2:rdiscinf
  column: TO_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyTO_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# to date

**Semantic key:** `to_date` · **Cột vật lý:** `TO_DATE`

## Ý nghĩa nghiệp vụ

Ngày kết thúc hiệu lực (to date).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `TO_DATE` | datetime | NgàyTO_DATE |
| `db2:rdiscinf` | `TO_DATE` | datetime | NgàyTO_DATE |

## Ghi chú thêm

- NgàyTO_DATE
