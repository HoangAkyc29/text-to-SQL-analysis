---
semantic_key: updated
title: updated
display_names:
- UPDATED
kind: date
tables:
- ref: db1:pmtrans
  column: UPDATED
  type: bit
- ref: db1:strans
  column: UPDATED
  type: bit
- ref: db1:transhdr_arc
  column: UPDATED
  type: bit
- ref: db2:pmtrans
  column: UPDATED
  type: bit
- ref: db2:st_order
  column: UPDATED
  type: bit
- ref: db2:strans
  column: UPDATED
  type: bit
- ref: db2:strans_tmp
  column: UPDATED
  type: bit
- ref: db2:suspend
  column: UPDATED
  type: bit
- ref: db2:transhdr
  column: UPDATED
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Đã cập nhật (bit)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.UPDATED: top=False(1000)'
- 'db1:strans.UPDATED: top=True(974), False(26)'
- 'db1:transhdr_arc.UPDATED: top=False(1000)'
- 'db2:pmtrans.UPDATED: top=False(1000)'
- 'db2:st_order.UPDATED: top=False(1000)'
- 'db2:strans.UPDATED: top=True(1000)'
- 'db2:strans_tmp.UPDATED: top=True(1000)'
- 'db2:suspend.UPDATED: top=False(1000)'
- 'db2:transhdr.UPDATED: top=False(1000)'
---

# updated

**Semantic key:** `updated` · **Cột vật lý:** `UPDATED`

## Ý nghĩa nghiệp vụ

Cột UPDATED trên PMTRANS, STRANS, STRANS_TMP. db1:pmtrans: top False; db1:strans: top True; db1:transhdr_arc: top False; db2:pmtrans: top False; db2:st_order: top False; db2:strans: top True; db2:strans_tmp: top True; db2:suspend: top False; db2:transhdr: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `UPDATED` | bit | có dữ liệu |
| `db1:strans` | `UPDATED` | bit | có dữ liệu |
| `db1:transhdr_arc` | `UPDATED` | bit | có dữ liệu |
| `db2:pmtrans` | `UPDATED` | bit | có dữ liệu |
| `db2:st_order` | `UPDATED` | bit | có dữ liệu |
| `db2:strans` | `UPDATED` | bit | có dữ liệu |
| `db2:strans_tmp` | `UPDATED` | bit | có dữ liệu |
| `db2:suspend` | `UPDATED` | bit | có dữ liệu |
| `db2:transhdr` | `UPDATED` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db1:strans.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db1:transhdr_arc.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:pmtrans.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:st_order.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:strans.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:strans_tmp.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:suspend.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:transhdr.UPDATED`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Đã cập nhật (bit)
