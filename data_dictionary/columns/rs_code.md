---
semantic_key: rs_code
title: rs code
display_names:
- RS_CODE
kind: code
tables:
- ref: db1:strans
  column: RS_CODE
  type: char
- ref: db2:pmcrdstk
  column: RS_CODE
  type: char
- ref: db2:strans
  column: RS_CODE
  type: char
- ref: db2:strans_tmp
  column: RS_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã lý do (hủy, trả, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.RS_CODE: top=08(143), 01(24), 02(20), 03(17)'
- 'db2:pmcrdstk.RS_CODE: top=01(1)'
- 'db2:strans.RS_CODE: top=08(61), 03(37), 01(16)'
- 'db2:strans_tmp.RS_CODE: top=02(1)'
---

# rs code

**Semantic key:** `rs_code` · **Cột vật lý:** `RS_CODE`

## Ý nghĩa nghiệp vụ

Cột RS_CODE trên PMCRDSTK, STRANS, STRANS_TMP. db1:strans: top 01, 03; db2:strans: top 03, 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `RS_CODE` | char | có dữ liệu |
| `db2:pmcrdstk` | `RS_CODE` | char | có dữ liệu |
| `db2:strans` | `RS_CODE` | char | có dữ liệu |
| `db2:strans_tmp` | `RS_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.RS_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `01`×10, `03`×10

### `db2:strans.RS_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `03`×16, `01`×4

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã lý do (hủy, trả, …)
