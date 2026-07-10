---
semantic_key: sex
title: Giới tính khách hàng (SEX)
display_names:
- SEX
kind: text
tables:
- ref: db2:cscard
  column: SEX
  type: char
- ref: db2:customer
  column: SEX
  type: char
join_with: []
related_semantic_keys: []
facts:
- Giới tính
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giới tính khách hàng (SEX)

**Semantic key:** `sex` · **Cột vật lý:** `SEX`

## Ý nghĩa nghiệp vụ

Giới tính. Dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (CUSTOMER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `SEX` | char | Giới tính |
| `db2:customer` | `SEX` | char | Giới tính |
