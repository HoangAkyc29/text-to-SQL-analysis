---
semantic_key: mdisc_amt
title: mdisc amt
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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MDISC_AMT: top=0.00(984), 30000.00(2), 1500.00(2), 16000.00(1), 5000.00(1)'
- 'db2:inv_hdr.MDISC_AMT: top=0.00(1000)'
- 'db2:st_order.MDISC_AMT: top=0(1000)'
- 'db2:strans.MDISC_AMT: top=0.00(998), 74640.00(1), 96048.00(1)'
- 'db2:strans_tmp.MDISC_AMT: top=0.00(993), 16000.00(1), 5000.00(1), 8100.00(1), 20616.00(1)'
- 'db2:suspend.MDISC_AMT: top=0.00(990), 3000.00(2), 32016.00(1), 5200.00(1), 14000.00(1)'
---

# mdisc amt

**Semantic key:** `mdisc_amt` · **Cột vật lý:** `MDISC_AMT`

## Ý nghĩa nghiệp vụ

Cột MDISC_AMT trên INV_HDR, STRANS, STRANS_TMP. db1:strans: top 0.00; db2:inv_hdr: top 0.00; db2:st_order: top 0; db2:strans: top 0.00, 1526000.00, 133000.01; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MDISC_AMT` | numeric | có dữ liệu |
| `db2:inv_hdr` | `MDISC_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `MDISC_AMT` | numeric | có dữ liệu |
| `db2:strans` | `MDISC_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `MDISC_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `MDISC_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.MDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:inv_hdr.MDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.MDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.MDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈6; top: `0.00`×15, `1526000.00`×1, `133000.01`×1, `36944.45`×1, `56388.89`×1, `38888.89`×1

### `db2:strans_tmp.MDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.MDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chiết khấu manual: MDISC_AMT
