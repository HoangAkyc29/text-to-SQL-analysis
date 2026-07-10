---
semantic_key: tran_time
title: Giờ giao dich (HH:MM trên POS) (TRAN_TIME)
display_names:
- TRAN_TIME
kind: date
tables:
- ref: db1:crdtrans_arc
  column: TRAN_TIME
  type: char
- ref: db1:pmtrans
  column: TRAN_TIME
  type: char
- ref: db1:strans
  column: TRAN_TIME
  type: char
- ref: db1:transhdr_arc
  column: TRAN_TIME
  type: char
- ref: db2:crdtrans
  column: TRAN_TIME
  type: char
- ref: db2:crdtrans_tmp
  column: TRAN_TIME
  type: char
- ref: db2:ctrans
  column: TRAN_TIME
  type: char
- ref: db2:pmcrdiss
  column: TRAN_TIME
  type: char
- ref: db2:pmcrdstk
  column: TRAN_TIME
  type: char
- ref: db2:pmtrans
  column: TRAN_TIME
  type: char
- ref: db2:st_order
  column: TRAN_TIME
  type: char
- ref: db2:strans
  column: TRAN_TIME
  type: char
- ref: db2:strans_tmp
  column: TRAN_TIME
  type: char
- ref: db2:suspend
  column: TRAN_TIME
  type: char
- ref: db2:transhdr
  column: TRAN_TIME
  type: char
join_with: []
related_semantic_keys: []
facts:
- Giờ giao dịch (HH:MM)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giờ giao dich (HH:MM trên POS) (TRAN_TIME)

**Semantic key:** `tran_time` · **Cột vật lý:** `TRAN_TIME`

## Ý nghĩa nghiệp vụ

Giờ giao dịch (HH:MM) trên POS — join cùng TRAN_DATE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db1:pmtrans` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db1:strans` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db1:transhdr_arc` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:crdtrans` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:crdtrans_tmp` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:ctrans` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:pmcrdiss` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:pmcrdstk` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:pmtrans` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:st_order` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:strans` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:strans_tmp` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:suspend` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
| `db2:transhdr` | `TRAN_TIME` | char | Giờ giao dịch (HH:MM) |
