---
semantic_key: activate
title: activate
display_names:
- ACTIVATE
kind: flag
tables:
- ref: db2:pmcrdinf
  column: ACTIVATE
  type: bit
- ref: db2:pmcrdstk
  column: ACTIVATE
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Đã kích hoạt
sources:
- table_md
- column_semantic_registry
- business_prose
---

# activate

**Semantic key:** `activate` · **Cột vật lý:** `ACTIVATE`

## Ý nghĩa nghiệp vụ

Đã kích hoạt. Dùng trong master thẻ PM / voucher, bảng PMCRDSTK.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `ACTIVATE` | bit | Đã kích hoạt |
| `db2:pmcrdstk` | `ACTIVATE` | bit | Đã kích hoạt |
