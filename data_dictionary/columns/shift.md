---
semantic_key: shift
title: Ca làm việc POS (SHIFT)
display_names:
- SHIFT
kind: measure
tables:
- ref: db1:pmtrans
  column: SHIFT
  type: numeric
- ref: db1:strans
  column: SHIFT
  type: numeric
- ref: db1:transhdr_arc
  column: SHIFT
  type: numeric
- ref: db2:cash_st
  column: SHIFT
  type: numeric
- ref: db2:inv_iss
  column: SHIFT
  type: numeric
- ref: db2:pmtrans
  column: SHIFT
  type: numeric
- ref: db2:st_order
  column: SHIFT
  type: numeric
- ref: db2:strans
  column: SHIFT
  type: numeric
- ref: db2:strans_tmp
  column: SHIFT
  type: numeric
- ref: db2:suspend
  column: SHIFT
  type: numeric
- ref: db2:transhdr
  column: SHIFT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Ca làm việc
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ca làm việc POS (SHIFT)

**Semantic key:** `shift` · **Cột vật lý:** `SHIFT`

## Ý nghĩa nghiệp vụ

Ca làm việc. Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Kho / mua hàng (INV_ISS, ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `SHIFT` | numeric | Ca làm việc |
| `db1:strans` | `SHIFT` | numeric | Ca làm việc |
| `db1:transhdr_arc` | `SHIFT` | numeric | Ca làm việc |
| `db2:cash_st` | `SHIFT` | numeric | Ca làm việc |
| `db2:inv_iss` | `SHIFT` | numeric | Ca làm việc |
| `db2:pmtrans` | `SHIFT` | numeric | Ca làm việc |
| `db2:st_order` | `SHIFT` | numeric | Ca làm việc |
| `db2:strans` | `SHIFT` | numeric | Ca làm việc |
| `db2:strans_tmp` | `SHIFT` | numeric | Ca làm việc |
| `db2:suspend` | `SHIFT` | numeric | Ca làm việc |
| `db2:transhdr` | `SHIFT` | numeric | Ca làm việc |
