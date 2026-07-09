---
semantic_key: mdisc_code
title: mdisc code
display_names:
- MDISC_CODE
kind: code
tables:
- ref: db1:strans
  column: MDISC_CODE
  type: char
- ref: db2:strans_tmp
  column: MDISC_CODE
  type: char
- ref: db2:suspend
  column: MDISC_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_CODE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MDISC_CODE: top=000125041801(3), 000125041901(2), 000125033101(2), 000125042101(1),
  000125041701(1)'
- 'db2:strans_tmp.MDISC_CODE: top=000124052401(3), 000124052501(1), 000124052801(1),
  000124042501(1)'
- 'db2:suspend.MDISC_CODE: top=000120122301(1), 000125041801(1), 000124042501(1),
  000122122501(1), 000125041702(1)'
---

# mdisc code

**Semantic key:** `mdisc_code` · **Cột vật lý:** `MDISC_CODE`

## Ý nghĩa nghiệp vụ

Chiết khấu manual: MDISC_CODE

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MDISC_CODE` | char | có dữ liệu |
| `db2:strans_tmp` | `MDISC_CODE` | char | có dữ liệu |
| `db2:suspend` | `MDISC_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

