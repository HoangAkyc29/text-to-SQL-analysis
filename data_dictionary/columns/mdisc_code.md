---
semantic_key: mdisc_code
title: mdisc code
display_names:
- MDISC_CODE
kind: code
tables:
- ref: db1:strans
  column: MDISC_CODE
  type: char
- ref: db2:strans_tmp
  column: MDISC_CODE
  type: char
- ref: db2:suspend
  column: MDISC_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_CODE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# mdisc code

**Semantic key:** `mdisc_code` · **Cột vật lý:** `MDISC_CODE`

## Ý nghĩa nghiệp vụ

Chiết khấu manual: MDISC_CODE. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MDISC_CODE` | char | Chiết khấu manual: MDISC_CODE |
| `db2:strans_tmp` | `MDISC_CODE` | char | Chiết khấu manual: MDISC_CODE |
| `db2:suspend` | `MDISC_CODE` | char | Chiết khấu manual: MDISC_CODE |

## Join

Thường join: `TRANS_NUM`
