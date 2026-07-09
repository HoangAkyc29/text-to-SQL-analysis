---
semantic_key: surplus
title: surplus
display_names:
- SURPLUS
kind: measure
tables:
- ref: db1:strans
  column: SURPLUS
  type: numeric
- ref: db1:transhdr_arc
  column: SURPLUS
  type: numeric
- ref: db2:st_order
  column: SURPLUS
  type: decimal
- ref: db2:strans
  column: SURPLUS
  type: numeric
- ref: db2:strans_tmp
  column: SURPLUS
  type: numeric
- ref: db2:suspend
  column: SURPLUS
  type: numeric
- ref: db2:transhdr
  column: SURPLUS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Phụ phí / surplus
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.SURPLUS: top=0.00(205), 8000.00(10), 10000.00(6), 25000.00(5), 15000.00(5)'
- 'db1:transhdr_arc.SURPLUS: top=0.00(62), 8000.00(4), 5000.00(4), 18000.00(3), 6000.00(3)'
- 'db2:st_order.SURPLUS: top=0.00(1000)'
- 'db2:strans.SURPLUS: top=0.00(138), 49.02(20), -650.93(17), -88.89(15), -232.88(10)'
- 'db2:strans_tmp.SURPLUS: top=10000.00(13), 1.00(10), 15000.00(10), 8000.00(8), 28000.00(7)'
- 'db2:suspend.SURPLUS: top=0.00(1000)'
- 'db2:transhdr.SURPLUS: top=0.00(47), 11033.33(3), 925.93(3), 1280.98(3), 6523.78(3)'
---

# surplus

**Semantic key:** `surplus` · **Cột vật lý:** `SURPLUS`

## Ý nghĩa nghiệp vụ

Cột SURPLUS trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db1:transhdr_arc: top 7591.95, 64438.17, 35145.48; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 871347.26, 503207.17, 787119.38; db2:suspend: top 0.00; db2:transhdr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `SURPLUS` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `SURPLUS` | numeric | có dữ liệu |
| `db2:st_order` | `SURPLUS` | decimal | có dữ liệu |
| `db2:strans` | `SURPLUS` | numeric | có dữ liệu |
| `db2:strans_tmp` | `SURPLUS` | numeric | có dữ liệu |
| `db2:suspend` | `SURPLUS` | numeric | có dữ liệu |
| `db2:transhdr` | `SURPLUS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db1:transhdr_arc.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈20; top: `7591.95`×1, `64438.17`×1, `35145.48`×1, `16608.93`×1, `145908.98`×1, `5383.85`×1, `5547.39`×1, `19491.57`×1

### `db2:st_order.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈20; top: `871347.26`×1, `503207.17`×1, `787119.38`×1, `696507.93`×1, `82020.19`×1, `83333.31`×1, `47222.22`×1, `1064.60`×1

### `db2:suspend.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.SURPLUS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Phụ phí / surplus
