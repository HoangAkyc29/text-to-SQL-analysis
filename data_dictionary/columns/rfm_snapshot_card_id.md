---
semantic_key: rfm_snapshot_card_id
title: rfm snapshot card id
display_names:
- card_id
kind: identifier
tables:
- ref: db2:webrpt_rfm_snapshot
  column: card_id
  type: varchar
join_with:
- TRANS_NUM
- CUST_ID
related_semantic_keys: []
facts:
- Mã thẻ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_rfm_snapshot.card_id: top=A10000073374(1), A10000048872(1), A10000057214(1),
  A10000076512(1), E10000003257(1)'
---

# rfm snapshot card id

**Semantic key:** `rfm_snapshot_card_id` · **Cột vật lý:** `card_id`

## Ý nghĩa nghiệp vụ

Cột CARD_ID trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: prefix A (vd. A10000003872).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `card_id` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.card_id`
- Null rate trong sample: 0%
- Distinct ≈20; top: `A10000003872`×1, `A10000004618`×1, `A10000005616`×1, `A10000005661`×1, `A10000006303`×1, `A10000006307`×1, `A10000006455`×1, `A10000006489`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ
