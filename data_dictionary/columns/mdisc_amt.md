---
semantic_key: mdisc_amt
title: Chiết khấu khuyến mãi (MDISC_AMT)
display_names:
- MDISC_AMT
kind: measure
tables:
- ref: db1:strans
  column: MDISC_AMT
  type: numeric
- ref: db2:inv_hdr
  column: MDISC_AMT
  type: numeric
- ref: db2:st_order
  column: MDISC_AMT
  type: numeric
- ref: db2:strans
  column: MDISC_AMT
  type: numeric
- ref: db2:strans_tmp
  column: MDISC_AMT
  type: numeric
- ref: db2:suspend
  column: MDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Chiết khấu khuyến mãi (MDISC_AMT)

**Semantic key:** `mdisc_amt` · **Cột vật lý:** `MDISC_AMT`

## Ý nghĩa nghiệp vụ

Số tiền chiết khấu khuyến mãi (MDISC) — thường trên STRANS / đơn KM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MDISC_AMT` | numeric | Chiết khấu manual: MDISC_AMT |
| `db2:inv_hdr` | `MDISC_AMT` | numeric | Chiết khấu manual: MDISC_AMT |
| `db2:st_order` | `MDISC_AMT` | numeric | Chiết khấu manual: MDISC_AMT |
| `db2:strans` | `MDISC_AMT` | numeric | Chiết khấu manual: MDISC_AMT |
| `db2:strans_tmp` | `MDISC_AMT` | numeric | Chiết khấu manual: MDISC_AMT |
| `db2:suspend` | `MDISC_AMT` | numeric | Chiết khấu manual: MDISC_AMT |

## Ghi chú thêm

- Chiết khấu manual: MDISC_AMT
