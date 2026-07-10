---
semantic_key: email
title: Email liên hệ (EMAIL)
display_names:
- EMAIL
kind: text
tables:
- ref: db2:cscard
  column: EMAIL
  type: varchar
- ref: db2:customer
  column: EMAIL
  type: varchar
- ref: db2:inv_iss
  column: EMAIL
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Email
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Email liên hệ (EMAIL)

**Semantic key:** `email` · **Cột vật lý:** `EMAIL`

## Ý nghĩa nghiệp vụ

Email liên hệ khách trên master CUSTOMER / CSCARD.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `EMAIL` | varchar | Email |
| `db2:customer` | `EMAIL` | varchar | Email |
| `db2:inv_iss` | `EMAIL` | varchar | Email |
