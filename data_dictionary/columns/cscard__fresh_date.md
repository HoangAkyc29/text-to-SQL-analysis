---
semantic_key: cscard__fresh_date
title: Ngày fresh (CSCARD)
display_names:
- FRESH_DATE
kind: date
tables:
- ref: db2:cscard
  column: FRESH_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyFRESH_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày fresh (CSCARD)

**Semantic key:** `cscard__fresh_date` · **Cột vật lý:** `FRESH_DATE`

## Ý nghĩa nghiệp vụ

Ngày làm mới / cập nhật trạng thái thẻ gần nhất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `FRESH_DATE` | datetime | NgàyFRESH_DATE |

## Ghi chú thêm

- NgàyFRESH_DATE
