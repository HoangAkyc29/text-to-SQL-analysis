---
semantic_key: due_date
title: Ngày đến hạn (DUE_DATE)
display_names:
- DUE_DATE
kind: date
tables:
- ref: db1:strans
  column: DUE_DATE
  type: datetime
- ref: db1:transhdr_arc
  column: DUE_DATE
  type: datetime
- ref: db2:cscard
  column: DUE_DATE
  type: datetime
- ref: db2:ctrans
  column: DUE_DATE
  type: datetime
- ref: db2:customer
  column: DUE_DATE
  type: datetime
- ref: db2:debt
  column: DUE_DATE
  type: datetime
- ref: db2:pmcrdinf
  column: DUE_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: DUE_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: DUE_DATE
  type: datetime
- ref: db2:strans
  column: DUE_DATE
  type: datetime
- ref: db2:transhdr
  column: DUE_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Hạn thanh toán / hạn giao
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày đến hạn (DUE_DATE)

**Semantic key:** `due_date` · **Cột vật lý:** `DUE_DATE`

## Ý nghĩa nghiệp vụ

Ngày đến hạn thanh toán / giao hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db1:transhdr_arc` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:cscard` | `DUE_DATE` | datetime | Ngày hết hạn thẻ |
| `db2:ctrans` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:customer` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:debt` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:pmcrdinf` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:pmcrdiss` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:pmcrdstk` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:strans` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |
| `db2:transhdr` | `DUE_DATE` | datetime | Hạn thanh toán / hạn giao |

## Ghi chú thêm

- Hạn thanh toán / hạn giao
