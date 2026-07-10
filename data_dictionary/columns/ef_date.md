---
semantic_key: ef_date
title: Ngày hiệu lực (EF_DATE)
display_names:
- EF_DATE
kind: date
tables:
- ref: db1:strans
  column: EF_DATE
  type: datetime
- ref: db1:transhdr_arc
  column: EF_DATE
  type: datetime
- ref: db2:cscard
  column: EF_DATE
  type: datetime
- ref: db2:ctrans
  column: EF_DATE
  type: datetime
- ref: db2:st_order
  column: EF_DATE
  type: datetime
- ref: db2:strans
  column: EF_DATE
  type: datetime
- ref: db2:strans_tmp
  column: EF_DATE
  type: datetime
- ref: db2:suspend
  column: EF_DATE
  type: datetime
- ref: db2:transhdr
  column: EF_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày hiệu lực
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày hiệu lực (EF_DATE)

**Semantic key:** `ef_date` · **Cột vật lý:** `EF_DATE`

## Ý nghĩa nghiệp vụ

Ngày hiệu lực bản ghi / chứng từ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db1:transhdr_arc` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:cscard` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:ctrans` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:st_order` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:strans` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:strans_tmp` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:suspend` | `EF_DATE` | datetime | Ngày hiệu lực |
| `db2:transhdr` | `EF_DATE` | datetime | Ngày hiệu lực |
