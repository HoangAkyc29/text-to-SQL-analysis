---
semantic_key: mdisc_type
title: mdisc type
display_names:
- MDISC_TYPE
kind: text
tables:
- ref: db1:strans
  column: MDISC_TYPE
  type: char
- ref: db2:strans
  column: MDISC_TYPE
  type: char
- ref: db2:strans_tmp
  column: MDISC_TYPE
  type: char
- ref: db2:suspend
  column: MDISC_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_TYPE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MDISC_TYPE: top=02(9), 01(6), 03(1)'
- 'db2:strans.MDISC_TYPE: top=01(1), 03(1)'
- 'db2:strans_tmp.MDISC_TYPE: top=02(5), 03(2)'
- 'db2:suspend.MDISC_TYPE: top=02(5), 03(4), 01(1)'
---

# mdisc type

**Semantic key:** `mdisc_type` · **Cột vật lý:** `MDISC_TYPE`

## Ý nghĩa nghiệp vụ

Cột MDISC_TYPE trên STRANS, STRANS_TMP, SUSPEND. db2:strans: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MDISC_TYPE` | char | có dữ liệu |
| `db2:strans` | `MDISC_TYPE` | char | có dữ liệu |
| `db2:strans_tmp` | `MDISC_TYPE` | char | có dữ liệu |
| `db2:suspend` | `MDISC_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:strans.MDISC_TYPE`
- Null rate trong sample: 75%
- Distinct ≈1; top: `01`×5

## Ghi chú thêm

- Chiết khấu manual: MDISC_TYPE
