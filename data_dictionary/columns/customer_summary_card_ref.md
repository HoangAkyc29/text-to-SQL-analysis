---
semantic_key: customer_summary_card_ref
title: customer summary card ref
display_names:
- Card_ID
kind: identifier
tables:
- ref: db2:custsumm
  column: Card_ID
  type: char
join_with:
- TRANS_NUM
- CUST_ID
related_semantic_keys: []
facts:
- Cột Card_ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:custsumm.Card_ID: top=d10000001337(1), A10000059469(1), e10000001186(1), A10000062068(1),
  e10000003087(1)'
---

# customer summary card ref

**Semantic key:** `customer_summary_card_ref` · **Cột vật lý:** `Card_ID`

## Ý nghĩa nghiệp vụ

Cột CARD_ID trên CUSTSUMM. db2:custsumm: prefix Hh (vd. H10000002162).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:custsumm` | `Card_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:custsumm.Card_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `H10000002162`×1, `h10000001785`×1, `h10000002107`×1, `h10000002182`×1, `h10000002546`×1, `H10000002212`×1, `H10000002432`×1, `h10000002364`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Cột Card_ID
