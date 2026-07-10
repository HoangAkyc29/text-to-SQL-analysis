---
semantic_key: kit_id
title: Mã bộ kit / combo kit (KIT_ID)
display_names:
- KIT_ID
kind: identifier
tables:
- ref: db2:strans
  column: KIT_ID
  type: char
- ref: db2:strans_tmp
  column: KIT_ID
  type: char
- ref: db2:suspend
  column: KIT_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã kit
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã bộ kit / combo kit (KIT_ID)

**Semantic key:** `kit_id` · **Cột vật lý:** `KIT_ID`

## Ý nghĩa nghiệp vụ

Mã kit. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:strans` | `KIT_ID` | char | Mã kit |
| `db2:strans_tmp` | `KIT_ID` | char | Mã kit |
| `db2:suspend` | `KIT_ID` | char | Mã kit |
