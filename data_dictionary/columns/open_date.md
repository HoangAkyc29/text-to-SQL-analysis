---
semantic_key: open_date
title: Ngày mở / ngày tạo bản ghi (OPEN_DATE)
display_names:
- OPEN_DATE
kind: date
tables:
- ref: db2:account
  column: OPEN_DATE
  type: datetime
- ref: db2:crd_info
  column: OPEN_DATE
  type: datetime
- ref: db2:cscard
  column: OPEN_DATE
  type: datetime
- ref: db2:customer
  column: OPEN_DATE
  type: datetime
- ref: db2:partner
  column: OPEN_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: OPEN_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: OPEN_DATE
  type: datetime
- ref: db2:sku_def
  column: OPEN_DATE
  type: datetime
- ref: db2:supplier
  column: OPEN_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày mở / tạo
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày mở / ngày tạo bản ghi (OPEN_DATE)

**Semantic key:** `open_date` · **Cột vật lý:** `OPEN_DATE`

## Ý nghĩa nghiệp vụ

Ngày mở / tạo bản ghi master hoặc chứng từ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:crd_info` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:cscard` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:customer` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:partner` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:pmcrdiss` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:pmcrdstk` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:sku_def` | `OPEN_DATE` | datetime | Ngày mở / tạo |
| `db2:supplier` | `OPEN_DATE` | datetime | Ngày mở / tạo |
