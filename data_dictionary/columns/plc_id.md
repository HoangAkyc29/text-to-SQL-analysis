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
- column_semantic_registry
- business_prose
---

# plc id

**Semantic key:** `plc_id` · **Cột vật lý:** `PLC_ID`

## Ý nghĩa nghiệp vụ

Mã địa phương. Dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (CUSTOMER, PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `PLC_ID` | char | Mã địa phương |
| `db2:customer` | `PLC_ID` | char | Mã địa phương |
| `db2:partner` | `PLC_ID` | char | Mã địa phương |
