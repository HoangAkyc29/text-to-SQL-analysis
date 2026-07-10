---
semantic_key: comm_amt
title: Tiền hoa hồng (COMM_AMT)
display_names:
- COMM_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: COMM_AMT
  type: numeric
- ref: db1:strans
  column: COMM_AMT
  type: numeric
- ref: db1:transhdr_arc
  column: COMM_AMT
  type: numeric
- ref: db2:crdtrans
  column: COMM_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: COMM_AMT
  type: numeric
- ref: db2:custhist
  column: COMM_AMT
  type: numeric
- ref: db2:st_order
  column: COMM_AMT
  type: decimal
- ref: db2:strans
  column: COMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: COMM_AMT
  type: numeric
- ref: db2:suspend
  column: COMM_AMT
  type: numeric
- ref: db2:transhdr
  column: COMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tiền hoa hồng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tiền hoa hồng (COMM_AMT)

**Semantic key:** `comm_amt` · **Cột vật lý:** `COMM_AMT`

## Ý nghĩa nghiệp vụ

Tiền hoa hồng ghi trên dòng bán hoặc giao dịch loyalty — thường populate khi có chương trình hoa hồng / coupon liên kết.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `COMM_AMT` | numeric | Tiền hoa hồng |
| `db1:strans` | `COMM_AMT` | numeric | hoa hồng trên dòng bán |
| `db1:transhdr_arc` | `COMM_AMT` | numeric | Tiền hoa hồng |
| `db2:crdtrans` | `COMM_AMT` | numeric | hoa hồng gắn giao dịch tích điểm |
| `db2:crdtrans_tmp` | `COMM_AMT` | numeric | Tiền hoa hồng |
| `db2:custhist` | `COMM_AMT` | numeric | Tiền hoa hồng |
| `db2:st_order` | `COMM_AMT` | decimal | Tiền hoa hồng |
| `db2:strans` | `COMM_AMT` | numeric | hoa hồng trên dòng bán |
| `db2:strans_tmp` | `COMM_AMT` | numeric | Tiền hoa hồng |
| `db2:suspend` | `COMM_AMT` | numeric | Tiền hoa hồng |
| `db2:transhdr` | `COMM_AMT` | numeric | Tiền hoa hồng |
