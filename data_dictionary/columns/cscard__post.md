---
semantic_key: cscard__post
title: cscard · post
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for POST
- 'db2:cscard.POST: top=D(35)'
---

# cscard · post

**Semantic key:** `cscard__post` · **Cột vật lý:** `POST`

## Ý nghĩa nghiệp vụ

Cột POST trên CSCARD. db2:cscard: top D.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `POST` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.POST`
- Null rate trong sample: 15%
- Distinct ≈1; top: `D`×17

## Ghi chú thêm

- Trạng thái post chứng từ
