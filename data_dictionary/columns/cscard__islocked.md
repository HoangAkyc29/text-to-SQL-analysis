---
semantic_key: cscard__islocked
title: Cờ thuộc tính (locked) (CSCARD)
display_names:
- ISLOCKED
kind: flag
tables:
- ref: db2:cscard
  column: ISLOCKED
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (locked) (CSCARD)

**Semantic key:** `cscard__islocked` · **Cột vật lý:** `ISLOCKED`

## Ý nghĩa nghiệp vụ

Cờ khóa thẻ — thẻ bị khóa không tích/đổi điểm.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `ISLOCKED` | bit | Cờ thuộc tính (locked) trên master thẻ khách hàng thân thiết |
