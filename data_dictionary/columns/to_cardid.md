---
semantic_key: to_cardid
title: to cardid
display_names:
- TO_CARDID
kind: text
tables:
- ref: db2:pmcrdiss
  column: TO_CARDID
  type: char
- ref: db2:pmcrdstk
  column: TO_CARDID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Thẻ PM đích
sources:
- table_md
- column_semantic_registry
- business_prose
---

# to cardid

**Semantic key:** `to_cardid` · **Cột vật lý:** `TO_CARDID`

## Ý nghĩa nghiệp vụ

Thẻ PM đích. Dùng trong bảng PMCRDISS, bảng PMCRDSTK.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdiss` | `TO_CARDID` | char | Thẻ PM đích |
| `db2:pmcrdstk` | `TO_CARDID` | char | Thẻ PM đích |
