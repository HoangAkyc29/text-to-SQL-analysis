---
semantic_key: tran_date
title: Ngày giao dịch (TRAN_DATE)
display_names:
- TRAN_DATE
kind: date
tables:
- ref: db1:crdtrans_arc
  column: TRAN_DATE
  type: datetime
- ref: db1:pmtrans
  column: TRAN_DATE
  type: datetime
- ref: db1:strans
  column: TRAN_DATE
  type: datetime
- ref: db1:transhdr_arc
  column: TRAN_DATE
  type: datetime
- ref: db2:cash_st
  column: TRAN_DATE
  type: datetime
- ref: db2:crdtrans
  column: TRAN_DATE
  type: datetime
- ref: db2:crdtrans_tmp
  column: TRAN_DATE
  type: datetime
- ref: db2:ctrans
  column: TRAN_DATE
  type: datetime
- ref: db2:custhist
  column: TRAN_DATE
  type: datetime
- ref: db2:inv_iss
  column: TRAN_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: TRAN_DATE
  type: datetime
- ref: db2:pmcrdrcv
  column: TRAN_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: TRAN_DATE
  type: datetime
- ref: db2:pmtrans
  column: TRAN_DATE
  type: datetime
- ref: db2:st_order
  column: TRAN_DATE
  type: datetime
- ref: db2:strans
  column: TRAN_DATE
  type: datetime
- ref: db2:strans_tmp
  column: TRAN_DATE
  type: datetime
- ref: db2:suspend
  column: TRAN_DATE
  type: datetime
- ref: db2:transhdr
  column: TRAN_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày giao dịch; chọn shard db1 theo YYYYMM
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày giao dịch (TRAN_DATE)

**Semantic key:** `tran_date` · **Cột vật lý:** `TRAN_DATE`

## Ý nghĩa nghiệp vụ

Ngày giao dịch — cutoff db2 live vs db1 archive tùy bảng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `TRAN_DATE` | datetime | Ngày giao dịch; chọn shard db1 theo YYYYMM |
| `db1:pmtrans` | `TRAN_DATE` | datetime | Ngày giao dịch; chọn shard db1 theo YYYYMM |
| `db1:strans` | `TRAN_DATE` | datetime | Ngày giao dịch; chọn shard db1 theo YYYYMM |
| `db1:transhdr_arc` | `TRAN_DATE` | datetime | Ngày giao dịch; chọn shard db1 theo YYYYMM |
| `db2:cash_st` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:crdtrans` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:crdtrans_tmp` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:ctrans` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:custhist` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:inv_iss` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:pmcrdiss` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:pmcrdrcv` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:pmcrdstk` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:pmtrans` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:st_order` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:strans` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:strans_tmp` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:suspend` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |
| `db2:transhdr` | `TRAN_DATE` | datetime | Ngày giao dịch (bảng live db2, không shard) |

## Ghi chú thêm

- Ngày giao dịch; chọn shard db1 theo YYYYMM
