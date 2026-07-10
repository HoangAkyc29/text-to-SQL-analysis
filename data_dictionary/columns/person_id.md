---
semantic_key: person_id
title: Mã nhân viên / người liên hệ (PERSON_ID)
display_names:
- PERSON_ID
kind: identifier
tables:
- ref: db2:cscard
  column: PERSON_ID
  type: varchar
- ref: db2:customer
  column: PERSON_ID
  type: varchar
- ref: db2:inv_iss
  column: PERSON_ID
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- CMND/CCCD
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã nhân viên / người liên hệ (PERSON_ID)

**Semantic key:** `person_id` · **Cột vật lý:** `PERSON_ID`

## Ý nghĩa nghiệp vụ

CMND/CCCD. Dùng trong Loyalty / thẻ (CSCARD); Kho / mua hàng (INV_ISS); Master / danh mục (CUSTOMER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `PERSON_ID` | varchar | CMND/CCCD |
| `db2:customer` | `PERSON_ID` | varchar | CMND/CCCD |
| `db2:inv_iss` | `PERSON_ID` | varchar | CMND/CCCD |
