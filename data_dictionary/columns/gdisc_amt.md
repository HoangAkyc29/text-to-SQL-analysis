---
semantic_key: gdisc_amt
title: gdisc amt
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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.gdisc_amt: top=0.00(1000)'
- 'db2:st_order.GDISC_AMT: top=0.00(1000)'
- 'db2:strans.gdisc_amt: top=0.00(1000)'
- 'db2:strans_tmp.gdisc_amt: top=0.00(1000)'
---

# gdisc amt

**Semantic key:** `gdisc_amt` · **Cột vật lý:** `GDISC_AMT`, `gdisc_amt`

## Ý nghĩa nghiệp vụ

Cột GDISC_AMT trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `gdisc_amt` | numeric | có dữ liệu |
| `db2:st_order` | `GDISC_AMT` | numeric | có dữ liệu |
| `db2:strans` | `gdisc_amt` | numeric | có dữ liệu |
| `db2:strans_tmp` | `gdisc_amt` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.gdisc_amt`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.GDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.gdisc_amt`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.gdisc_amt`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chiết khấu gift/khuyến mãi: GDISC_AMT
