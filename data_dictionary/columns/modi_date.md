---
semantic_key: modi_date
title: Ngày cập nhật gần nhất (MODI_DATE)
display_names:
- MODI_DATE
kind: date
tables:
- ref: db2:customer
  column: MODI_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: MODI_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: MODI_DATE
  type: datetime
- ref: db2:sku_def
  column: MODI_DATE
  type: datetime
- ref: db2:supplier
  column: MODI_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày sửa gần nhất
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày cập nhật gần nhất (MODI_DATE)

**Semantic key:** `modi_date` · **Cột vật lý:** `MODI_DATE`

## Ý nghĩa nghiệp vụ

Ngày cập nhật / sửa gần nhất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `MODI_DATE` | datetime | Ngày sửa gần nhất |
| `db2:pmcrdiss` | `MODI_DATE` | datetime | Ngày sửa gần nhất |
| `db2:pmcrdstk` | `MODI_DATE` | datetime | Ngày sửa gần nhất |
| `db2:sku_def` | `MODI_DATE` | datetime | Ngày sửa gần nhất |
| `db2:supplier` | `MODI_DATE` | datetime | Ngày sửa gần nhất |

## Ghi chú thêm

- Ngày sửa gần nhất
