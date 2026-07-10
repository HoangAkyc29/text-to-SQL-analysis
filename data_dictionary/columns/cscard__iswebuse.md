---
semantic_key: cscard__iswebuse
title: Cờ thuộc tính (webuse) (CSCARD)
display_names:
- ISWEBUSE
kind: flag
tables:
- ref: db2:cscard
  column: ISWEBUSE
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (webuse) (CSCARD)

**Semantic key:** `cscard__iswebuse` · **Cột vật lý:** `ISWEBUSE`

## Ý nghĩa nghiệp vụ

Cờ cho phép dùng thẻ trên web / app.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `ISWEBUSE` | bit | Cờ thuộc tính (webuse) trên master thẻ khách hàng thân thiết |
