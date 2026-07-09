---
semantic_key: webrpt_rfm_snapshot__card_type
title: webrpt rfm snapshot · card type
display_names:
- card_type
kind: text
tables:
- ref: db2:webrpt_rfm_snapshot
  column: card_type
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Loại thẻ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for card_type
- 'db2:webrpt_rfm_snapshot.card_type: top=01(1000)'
---

# webrpt rfm snapshot · card type

**Semantic key:** `webrpt_rfm_snapshot__card_type` · **Cột vật lý:** `card_type`

## Ý nghĩa nghiệp vụ

Cột CARD_TYPE trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `card_type` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.card_type`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

## Ghi chú thêm

- Loại thẻ
