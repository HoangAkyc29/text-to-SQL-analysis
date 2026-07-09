---
semantic_key: person_id
title: person id
display_names:
- PERSON_ID
kind: identifier
tables:
- ref: db2:cscard
  column: PERSON_ID
  type: varchar
- ref: db2:customer
  column: PERSON_ID
  type: varchar
- ref: db2:inv_iss
  column: PERSON_ID
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- CMND/CCCD
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.PERSON_ID: top=0934806608(1), A10000047314(1), 653(1), 0778549337(1),
  0905995211(1)'
- 'db2:customer.PERSON_ID: top=11002140044(1), 750624(1), 0702314333(1), 9566566(1),
  565325632(1)'
- 'db2:inv_iss.PERSON_ID: top=059223366(5), 63640601(4), 666362225(3), 8799999999(3),
  20048319(2)'
---

# person id

**Semantic key:** `person_id` · **Cột vật lý:** `PERSON_ID`

## Ý nghĩa nghiệp vụ

Cột PERSON_ID trên CSCARD, CUSTOMER, INV_ISS. db2:cscard: top A10000000003, A10000000004, A10000000012; db2:customer: top E10000001281, E10000000003.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `PERSON_ID` | varchar | có dữ liệu |
| `db2:customer` | `PERSON_ID` | varchar | có dữ liệu |
| `db2:inv_iss` | `PERSON_ID` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.PERSON_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `A10000000003`×1, `A10000000004`×1, `A10000000012`×1, `A10000000021`×1, `A10000000038`×1, `A10000000044`×1, `A10000000106`×1, `A10000000156`×1

### `db2:customer.PERSON_ID`
- Null rate trong sample: 90%
- Distinct ≈2; top: `E10000001281`×1, `E10000000003`×1

## Ghi chú thêm

- CMND/CCCD
