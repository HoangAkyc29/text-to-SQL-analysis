---
semantic_key: rfm_snapshot_card_id
title: Mã thẻ khách hàng thân thiết (CARD_ID)
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
- column_semantic_registry
- business_prose
---

# Mã thẻ khách hàng thân thiết (CARD_ID)

**Semantic key:** `rfm_snapshot_card_id` · **Cột vật lý:** `card_id`

## Ý nghĩa nghiệp vụ

Mã thẻ trên snapshot RFM — join CSCARD/CRD_INFO. (bảng WEBRPT_RFM_SNAPSHOT).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_rfm_snapshot` | `card_id` | varchar | Mã thẻ |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`
