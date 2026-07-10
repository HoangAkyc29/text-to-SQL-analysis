---
semantic_key: disc_rate
title: Tỷ lệ chiết khấu (%) (DISC_RATE)
display_names:
- DISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: DISC_RATE
  type: numeric
- ref: db2:cscard
  column: DISC_RATE
  type: numeric
- ref: db2:customer
  column: DISC_RATE
  type: numeric
- ref: db2:plu
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdinf
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdiss
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdrcv
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdstk
  column: DISC_RATE
  type: numeric
- ref: db2:st_order
  column: DISC_RATE
  type: decimal
- ref: db2:strans
  column: DISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: DISC_RATE
  type: numeric
- ref: db2:supplier
  column: DISC_RATE
  type: numeric
- ref: db2:suspend
  column: DISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệ chiết khấu
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ chiết khấu (%) (DISC_RATE)

**Semantic key:** `disc_rate` · **Cột vật lý:** `DISC_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ chiết khấu (%) trên dòng hoặc bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:cscard` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:customer` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:plu` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:pmcrdinf` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:pmcrdiss` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:pmcrdrcv` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:pmcrdstk` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:st_order` | `DISC_RATE` | decimal | Tỷ lệ chiết khấu |
| `db2:strans` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:strans_tmp` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:supplier` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
| `db2:suspend` | `DISC_RATE` | numeric | Tỷ lệ chiết khấu |
