---
semantic_key: forex_cys
title: forex cys
display_names:
- FOREX_CYS
kind: text
tables:
- ref: db1:strans
  column: FOREX_CYS
  type: char
- ref: db2:strans
  column: FOREX_CYS
  type: char
- ref: db2:strans_tmp
  column: FOREX_CYS
  type: char
- ref: db2:suspend
  column: FOREX_CYS
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại tiền ngoại tệ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# forex cys

**Semantic key:** `forex_cys` · **Cột vật lý:** `FOREX_CYS`

## Ý nghĩa nghiệp vụ

Loại tiền ngoại tệ. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `FOREX_CYS` | char | Loại tiền ngoại tệ |
| `db2:strans` | `FOREX_CYS` | char | Loại tiền ngoại tệ |
| `db2:strans_tmp` | `FOREX_CYS` | char | Loại tiền ngoại tệ |
| `db2:suspend` | `FOREX_CYS` | char | Loại tiền ngoại tệ |
