---
semantic_key: pos_id
title: Mã quầy / POS terminal (POS_ID)
display_names:
- POS_ID
kind: identifier
tables:
- ref: db1:pmtrans
  column: POS_ID
  type: int
- ref: db2:cash_st
  column: POS_ID
  type: int
- ref: db2:pmtrans
  column: POS_ID
  type: int
join_with: []
related_semantic_keys: []
facts:
- Mã quầy POS
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã quầy / POS terminal (POS_ID)

**Semantic key:** `pos_id` · **Cột vật lý:** `POS_ID`

## Ý nghĩa nghiệp vụ

Mã quầy POS. Dùng trong POS bán lẻ (PMTRANS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `POS_ID` | int | Mã quầy POS |
| `db2:cash_st` | `POS_ID` | int | Mã quầy POS |
| `db2:pmtrans` | `POS_ID` | int | Mã quầy POS |
