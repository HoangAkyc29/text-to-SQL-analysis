---
semantic_key: gdisc_amt
title: Số tiền chiết khấu quà tặng (GDISC_AMT)
display_names:
- GDISC_AMT
- gdisc_amt
kind: measure
tables:
- ref: db1:strans
  column: gdisc_amt
  type: numeric
- ref: db2:st_order
  column: GDISC_AMT
  type: numeric
- ref: db2:strans
  column: gdisc_amt
  type: numeric
- ref: db2:strans_tmp
  column: gdisc_amt
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu gift/khuyến mãi: GDISC_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền chiết khấu quà tặng (GDISC_AMT)

**Semantic key:** `gdisc_amt` · **Cột vật lý:** `GDISC_AMT`, `gdisc_amt`

## Ý nghĩa nghiệp vụ

Chiết khấu gift/khuyến mãi: GDISC_AMT. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `gdisc_amt` | numeric | Số tiền chiết khấu quà tặng trên dòng bán hàng POS |
| `db2:st_order` | `GDISC_AMT` | numeric | Chiết khấu gift/khuyến mãi: GDISC_AMT |
| `db2:strans` | `gdisc_amt` | numeric | Số tiền chiết khấu quà tặng trên dòng bán hàng POS |
| `db2:strans_tmp` | `gdisc_amt` | numeric | Số tiền chiết khấu quà tặng trên dòng bán tạm / suspend |
