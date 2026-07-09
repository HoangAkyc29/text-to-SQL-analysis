---
semantic_key: plc_id
title: plc id
display_names:
- PLC_ID
kind: identifier
tables:
- ref: db2:cscard
  column: PLC_ID
  type: char
- ref: db2:customer
  column: PLC_ID
  type: char
- ref: db2:partner
  column: PLC_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã địa phương
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.PLC_ID: top=003301(113), 003301119(108), 001101(65), 001101251(41),
  003301123(5)'
- 'db2:customer.PLC_ID: top=003301(104), 003301119(98), 001101(66), 001101251(53),
  003301123(8)'
- 'db2:partner.PLC_ID: top=003301119(1), 003301121(1)'
---

# plc id

**Semantic key:** `plc_id` · **Cột vật lý:** `PLC_ID`

## Ý nghĩa nghiệp vụ

Cột PLC_ID trên CSCARD, CUSTOMER, PARTNER. db2:cscard: top 001101251.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `PLC_ID` | char | có dữ liệu |
| `db2:customer` | `PLC_ID` | char | có dữ liệu |
| `db2:partner` | `PLC_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.PLC_ID`
- Null rate trong sample: 95%
- Distinct ≈1; top: `001101251`×1

## Ghi chú thêm

- Mã địa phương
