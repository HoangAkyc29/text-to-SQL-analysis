---
semantic_key: phone
title: Số điện thoại (PHONE)
display_names:
- PHONE
- Phone
kind: text
tables:
- ref: db2:cscard
  column: PHONE
  type: varchar
- ref: db2:customer
  column: PHONE
  type: varchar
- ref: db2:custsumm
  column: Phone
  type: char
- ref: db2:inv_iss
  column: PHONE
  type: varchar
- ref: db2:partner
  column: PHONE
  type: varchar
- ref: db2:supplier
  column: PHONE
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Điện thoại
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số điện thoại (PHONE)

**Semantic key:** `phone` · **Cột vật lý:** `PHONE`, `Phone`

## Ý nghĩa nghiệp vụ

Số điện thoại liên hệ khách trên master hoặc snapshot tổng hợp.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `PHONE` | varchar | Điện thoại |
| `db2:customer` | `PHONE` | varchar | Điện thoại |
| `db2:custsumm` | `Phone` | char | Điện thoại |
| `db2:inv_iss` | `PHONE` | varchar | Điện thoại |
| `db2:partner` | `PHONE` | varchar | Điện thoại |
| `db2:supplier` | `PHONE` | varchar | Điện thoại |
