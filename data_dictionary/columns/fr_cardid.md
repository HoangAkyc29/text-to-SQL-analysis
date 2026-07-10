---
semantic_key: fr_cardid
title: fr cardid
display_names:
- FR_CARDID
kind: text
tables:
- ref: db2:pmcrdiss
  column: FR_CARDID
  type: char
- ref: db2:pmcrdstk
  column: FR_CARDID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Thẻ PM nguồn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# fr cardid

**Semantic key:** `fr_cardid` · **Cột vật lý:** `FR_CARDID`

## Ý nghĩa nghiệp vụ

Thẻ PM nguồn. Dùng trong bảng PMCRDISS, bảng PMCRDSTK.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdiss` | `FR_CARDID` | char | Thẻ PM nguồn |
| `db2:pmcrdstk` | `FR_CARDID` | char | Thẻ PM nguồn |
