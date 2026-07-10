---
semantic_key: mdisc_rate
title: Tỷ lệ chiết khấu khuyến mãi (%) (MDISC_RATE)
display_names:
- MDISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: MDISC_RATE
  type: numeric
- ref: db2:st_order
  column: MDISC_RATE
  type: numeric
- ref: db2:strans
  column: MDISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: MDISC_RATE
  type: numeric
- ref: db2:suspend
  column: MDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ chiết khấu khuyến mãi (%) (MDISC_RATE)

**Semantic key:** `mdisc_rate` · **Cột vật lý:** `MDISC_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ chiết khấu khuyến mãi (%) trên dòng / đơn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MDISC_RATE` | numeric | Chiết khấu manual: MDISC_RATE |
| `db2:st_order` | `MDISC_RATE` | numeric | Chiết khấu manual: MDISC_RATE |
| `db2:strans` | `MDISC_RATE` | numeric | Chiết khấu manual: MDISC_RATE |
| `db2:strans_tmp` | `MDISC_RATE` | numeric | Chiết khấu manual: MDISC_RATE |
| `db2:suspend` | `MDISC_RATE` | numeric | Chiết khấu manual: MDISC_RATE |

## Ghi chú thêm

- Chiết khấu manual: MDISC_RATE
