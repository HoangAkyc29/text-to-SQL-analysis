---
semantic_key: mdisc_type
title: mdisc type
display_names:
- MDISC_TYPE
kind: text
tables:
- ref: db1:strans
  column: MDISC_TYPE
  type: char
- ref: db2:strans
  column: MDISC_TYPE
  type: char
- ref: db2:strans_tmp
  column: MDISC_TYPE
  type: char
- ref: db2:suspend
  column: MDISC_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_TYPE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# mdisc type

**Semantic key:** `mdisc_type` · **Cột vật lý:** `MDISC_TYPE`

## Ý nghĩa nghiệp vụ

Chiết khấu manual: MDISC_TYPE. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MDISC_TYPE` | char | Chiết khấu manual: MDISC_TYPE |
| `db2:strans` | `MDISC_TYPE` | char | Chiết khấu manual: MDISC_TYPE |
| `db2:strans_tmp` | `MDISC_TYPE` | char | Chiết khấu manual: MDISC_TYPE |
| `db2:suspend` | `MDISC_TYPE` | char | Chiết khấu manual: MDISC_TYPE |
