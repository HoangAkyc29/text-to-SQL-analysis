---
semantic_key: assolst__isprocess
title: Cờ thuộc tính (process) (ASSOLST)
display_names:
- IsProcess
kind: flag
tables:
- ref: db2:assolst
  column: IsProcess
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (process) (ASSOLST)

**Semantic key:** `assolst__isprocess` · **Cột vật lý:** `IsProcess`

## Ý nghĩa nghiệp vụ

Cờ combo đang trong quy trình xử lý / duyệt — chưa active bán POS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:assolst` | `IsProcess` | bit | Cờ thuộc tính (process) trên master combo / bundle |
