---
semantic_key: last_date
title: last date
display_names:
- LAST_DATE
kind: date
tables:
- ref: db2:account
  column: LAST_DATE
  type: datetime
- ref: db2:crd_info
  column: LAST_DATE
  type: datetime
- ref: db2:cscard
  column: LAST_DATE
  type: datetime
- ref: db2:customer
  column: LAST_DATE
  type: datetime
- ref: db2:debt
  column: LAST_DATE
  type: datetime
- ref: db2:supplier
  column: LAST_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày giao dịch / cập nhật gần nhất
sources:
- table_md
- column_semantic_registry
- business_prose
---

# last date

**Semantic key:** `last_date` · **Cột vật lý:** `LAST_DATE`

## Ý nghĩa nghiệp vụ

Ngày giao dịch / cập nhật gần nhất. Dùng trong Loyalty / thẻ (CRD_INFO, CSCARD); Master / danh mục (CUSTOMER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `LAST_DATE` | datetime | Ngày giao dịch / cập nhật gần nhất |
| `db2:crd_info` | `LAST_DATE` | datetime | Ngày giao dịch / cập nhật gần nhất |
| `db2:cscard` | `LAST_DATE` | datetime | Ngày giao dịch / cập nhật gần nhất |
| `db2:customer` | `LAST_DATE` | datetime | Ngày giao dịch / cập nhật gần nhất |
| `db2:debt` | `LAST_DATE` | datetime | Ngày giao dịch / cập nhật gần nhất |
| `db2:supplier` | `LAST_DATE` | datetime | Ngày giao dịch / cập nhật gần nhất |
