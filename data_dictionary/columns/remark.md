---
semantic_key: remark
title: Ghi chú (REMARK)
display_names:
- REMARK
- Remark
kind: text
tables:
- ref: db1:pmtrans
  column: REMARK
  type: nvarchar
- ref: db1:strans
  column: REMARK
  type: nvarchar
- ref: db1:transhdr_arc
  column: REMARK
  type: nvarchar
- ref: db2:cscard
  column: REMARK
  type: nvarchar
- ref: db2:ctrans
  column: REMARK
  type: nvarchar
- ref: db2:customer
  column: REMARK
  type: nvarchar
- ref: db2:custsumm
  column: Remark
  type: nvarchar
- ref: db2:debt
  column: REMARK
  type: nvarchar
- ref: db2:inv_iss
  column: REMARK
  type: nvarchar
- ref: db2:partner
  column: REMARK
  type: nvarchar
- ref: db2:pmcrdiss
  column: REMARK
  type: nvarchar
- ref: db2:pmcrdstk
  column: REMARK
  type: nvarchar
- ref: db2:pmtrans
  column: REMARK
  type: nvarchar
- ref: db2:st_order
  column: REMARK
  type: nvarchar
- ref: db2:strans
  column: REMARK
  type: nvarchar
- ref: db2:supplier
  column: REMARK
  type: nvarchar
- ref: db2:transhdr
  column: REMARK
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Ghi chú nghiệp vụ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ghi chú (REMARK)

**Semantic key:** `remark` · **Cột vật lý:** `REMARK`, `Remark`

## Ý nghĩa nghiệp vụ

Ghi chú do nhân viên nhập trên chứng từ — CRDTRANS/CRDTRANS_ARC thường giải thích điều chỉnh điểm / đổi quà.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db1:strans` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db1:transhdr_arc` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:cscard` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:ctrans` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:customer` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:custsumm` | `Remark` | nvarchar | Ghi chú do nhân viên nhập trên bảng custsumm |
| `db2:debt` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:inv_iss` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:partner` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:pmcrdiss` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:pmcrdstk` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:pmtrans` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:st_order` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:strans` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:supplier` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:transhdr` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |

## Ghi chú thêm

- Ghi chú nghiệp vụ
