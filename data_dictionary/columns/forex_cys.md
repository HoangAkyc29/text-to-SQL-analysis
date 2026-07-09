---
semantic_key: forex_cys
title: forex cys
display_names:
- FOREX_CYS
kind: text
tables:
- ref: db1:strans
  column: FOREX_CYS
  type: char
- ref: db2:strans
  column: FOREX_CYS
  type: char
- ref: db2:strans_tmp
  column: FOREX_CYS
  type: char
- ref: db2:suspend
  column: FOREX_CYS
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại tiền ngoại tệ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.FOREX_CYS: top=VND(773)'
- 'db2:strans.FOREX_CYS: top=VND(874)'
- 'db2:strans_tmp.FOREX_CYS: top=VND(1000)'
- 'db2:suspend.FOREX_CYS: top=VND(1000)'
---

# forex cys

**Semantic key:** `forex_cys` · **Cột vật lý:** `FOREX_CYS`

## Ý nghĩa nghiệp vụ

Cột FOREX_CYS trên STRANS, STRANS_TMP, SUSPEND. db2:strans_tmp: top VND; db2:suspend: top VND.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `FOREX_CYS` | char | có dữ liệu |
| `db2:strans` | `FOREX_CYS` | char | có dữ liệu |
| `db2:strans_tmp` | `FOREX_CYS` | char | có dữ liệu |
| `db2:suspend` | `FOREX_CYS` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:strans_tmp.FOREX_CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

### `db2:suspend.FOREX_CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

## Ghi chú thêm

- Loại tiền ngoại tệ
