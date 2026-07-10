---
semantic_key: assolst__fix_ratio
title: Fix Ratio (ASSOLST)
display_names:
- FIX_RATIO
kind: flag
tables:
- ref: db2:assolst
  column: FIX_RATIO
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Fix Ratio (ASSOLST)

**Semantic key:** `assolst__fix_ratio` · **Cột vật lý:** `FIX_RATIO`

## Ý nghĩa nghiệp vụ

Cờ tỷ lệ cố định giữa các thành phần combo — không cho phép thay đổi tỷ lệ mix.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:assolst` | `FIX_RATIO` | bit | Cờ / trạng thái (fix ratio) trên master combo / bundle |
