---
semantic_key: cscard__post
title: Post (CSCARD)
display_names:
- POST
kind: text
tables:
- ref: db2:cscard
  column: POST
  type: char
join_with: []
related_semantic_keys: []
facts:
- Trạng thái post chứng từ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Post (CSCARD)

**Semantic key:** `cscard__post` · **Cột vật lý:** `POST`

## Ý nghĩa nghiệp vụ

Trạng thái post / duyệt thẻ trên master CSCARD.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `POST` | char | Trạng thái post chứng từ |

## Ghi chú thêm

- Trạng thái post chứng từ
