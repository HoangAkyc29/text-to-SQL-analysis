---
semantic_key: rs_code
title: rs code
display_names:
- RS_CODE
kind: code
tables:
- ref: db1:strans
  column: RS_CODE
  type: char
- ref: db2:pmcrdstk
  column: RS_CODE
  type: char
- ref: db2:strans
  column: RS_CODE
  type: char
- ref: db2:strans_tmp
  column: RS_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã lý do (hủy, trả, …)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# rs code

**Semantic key:** `rs_code` · **Cột vật lý:** `RS_CODE`

## Ý nghĩa nghiệp vụ

Mã lý do (hủy, trả, …). Dùng trong POS bán lẻ (STRANS, STRANS_TMP).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `RS_CODE` | char | Mã lý do (hủy, trả, …) |
| `db2:pmcrdstk` | `RS_CODE` | char | Mã lý do (hủy, trả, …) |
| `db2:strans` | `RS_CODE` | char | Mã lý do (hủy, trả, …) |
| `db2:strans_tmp` | `RS_CODE` | char | Mã lý do (hủy, trả, …) |

## Join

Thường join: `TRANS_NUM`
