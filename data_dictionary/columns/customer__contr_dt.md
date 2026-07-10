---
semantic_key: customer__contr_dt
title: Ngày contr (CUSTOMER)
display_names:
- CONTR_DT
kind: date
tables:
- ref: db2:customer
  column: CONTR_DT
  type: datetime
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày contr (CUSTOMER)

**Semantic key:** `customer__contr_dt` · **Cột vật lý:** `CONTR_DT`

## Ý nghĩa nghiệp vụ

Ngày contr — danh mục master khách hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `CONTR_DT` | datetime | Ngày contr trên danh mục master khách hàng |
