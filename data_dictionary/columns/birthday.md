---
semantic_key: birthday
title: Ngày sinh khách hàng (BIRTHDAY)
display_names:
- BIRTHDAY
kind: date
tables:
- ref: db2:cscard
  column: BIRTHDAY
  type: datetime
- ref: db2:customer
  column: BIRTHDAY
  type: datetime
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày sinh khách hàng (BIRTHDAY)

**Semantic key:** `birthday` · **Cột vật lý:** `BIRTHDAY`

## Ý nghĩa nghiệp vụ

Ngày sinh khách hàng trên master CUSTOMER / CSCARD — dùng phân khúc CRM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `BIRTHDAY` | datetime | Ngày sinh |
| `db2:customer` | `BIRTHDAY` | datetime | Ngày sinh khách hàng trên danh mục master khách hàng |
