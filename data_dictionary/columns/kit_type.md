---
semantic_key: kit_type
title: kit type
display_names:
- KIT_TYPE
kind: text
tables:
- ref: db2:strans
  column: KIT_TYPE
  type: char
- ref: db2:strans_tmp
  column: KIT_TYPE
  type: char
- ref: db2:suspend
  column: KIT_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# kit type

**Semantic key:** `kit_type` · **Cột vật lý:** `KIT_TYPE`

## Ý nghĩa nghiệp vụ

Thuộc tính kit type — dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:strans` | `KIT_TYPE` | char | Thuộc tính kit type trên dòng bán hàng POS |
| `db2:strans_tmp` | `KIT_TYPE` | char | Thuộc tính kit type trên dòng bán tạm / suspend |
| `db2:suspend` | `KIT_TYPE` | char | Thuộc tính kit type trên bill đang treo / chưa hoàn tất |
