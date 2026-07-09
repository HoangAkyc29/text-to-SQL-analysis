---
semantic_key: ostk_id
title: ostk id
display_names:
- OSTK_ID
kind: identifier
tables:
- ref: db1:strans
  column: OSTK_ID
  type: char
- ref: db2:st_order
  column: OSTK_ID
  type: char
- ref: db2:strans
  column: OSTK_ID
  type: char
- ref: db2:strans_tmp
  column: OSTK_ID
  type: char
- ref: db2:suspend
  column: OSTK_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Kho đích / kho đối ứng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.OSTK_ID: top=10001(10), 50971(7), 50724(7), 00062(6), 10005(6)'
- 'db2:st_order.OSTK_ID: top=10005(499), 10004(464), 10001(37)'
- 'db2:strans.OSTK_ID: top=50971(16), 50371(4), 50610(4), 10001(3), 40127(3)'
- 'db2:strans_tmp.OSTK_ID: top=230000029208(4), 230000011220(3), 230000011170(3),
  239010004903(3), 230000000634(3)'
- 'db2:suspend.OSTK_ID: top=230000000001(48), 230000029208(5), 230000000041(4), 230000008586(3),
  230000025238(3)'
---

# ostk id

**Semantic key:** `ostk_id` · **Cột vật lý:** `OSTK_ID`

## Ý nghĩa nghiệp vụ

Cột OSTK_ID trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 50565, 51550, 51547; db2:st_order: top 10005, 10004; db2:strans: top 50672, 50565, 51547; db2:strans_tmp: top 40003, 40010, 40004.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `OSTK_ID` | char | có dữ liệu |
| `db2:st_order` | `OSTK_ID` | char | có dữ liệu |
| `db2:strans` | `OSTK_ID` | char | có dữ liệu |
| `db2:strans_tmp` | `OSTK_ID` | char | có dữ liệu |
| `db2:suspend` | `OSTK_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.OSTK_ID`
- Null rate trong sample: 0%
- Distinct ≈4; top: `50565`×10, `51550`×5, `51547`×4, `51373`×1

### `db2:st_order.OSTK_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `10005`×17, `10004`×3

### `db2:strans.OSTK_ID`
- Null rate trong sample: 0%
- Distinct ≈4; top: `50672`×8, `50565`×7, `51547`×4, `51067`×1

### `db2:strans_tmp.OSTK_ID`
- Null rate trong sample: 0%
- Distinct ≈3; top: `40003`×10, `40010`×7, `40004`×3

## Ghi chú thêm

- Kho đích / kho đối ứng
