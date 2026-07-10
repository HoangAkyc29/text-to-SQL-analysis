---
semantic_key: cscard__changepwd
title: Changepwd (CSCARD)
display_names:
- CHANGEPWD
kind: flag
tables:
- ref: db2:cscard
  column: CHANGEPWD
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Changepwd (CSCARD)

**Semantic key:** `cscard__changepwd` · **Cột vật lý:** `CHANGEPWD`

## Ý nghĩa nghiệp vụ

Cờ bắt buộc đổi mật khẩu thẻ / PIN lần đăng nhập tới.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `CHANGEPWD` | bit | Cờ / trạng thái (changepwd) trên master thẻ khách hàng thân thiết |
