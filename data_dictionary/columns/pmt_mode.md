---
semantic_key: pmt_mode
title: pmt mode
display_names:
- PMT_MODE
kind: text
tables:
- ref: db1:strans
  column: PMT_MODE
  type: char
- ref: db1:transhdr_arc
  column: PMT_MODE
  type: char
- ref: db2:strans
  column: PMT_MODE
  type: char
- ref: db2:strans_tmp
  column: PMT_MODE
  type: char
- ref: db2:transhdr
  column: PMT_MODE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Chế độ thanh toán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.PMT_MODE: top=01(772), 02(1)'
- 'db1:transhdr_arc.PMT_MODE: top=01(939)'
- 'db2:strans.PMT_MODE: top=01(871)'
- 'db2:strans_tmp.PMT_MODE: top=01(1000)'
- 'db2:transhdr.PMT_MODE: top=01(952)'
---

# pmt mode

**Semantic key:** `pmt_mode` · **Cột vật lý:** `PMT_MODE`

## Ý nghĩa nghiệp vụ

Cột PMT_MODE trên STRANS, STRANS_TMP, TRANSHDR. db1:transhdr_arc: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `PMT_MODE` | char | có dữ liệu |
| `db1:transhdr_arc` | `PMT_MODE` | char | có dữ liệu |
| `db2:strans` | `PMT_MODE` | char | có dữ liệu |
| `db2:strans_tmp` | `PMT_MODE` | char | có dữ liệu |
| `db2:transhdr` | `PMT_MODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.PMT_MODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

## Ghi chú thêm

- Chế độ thanh toán
