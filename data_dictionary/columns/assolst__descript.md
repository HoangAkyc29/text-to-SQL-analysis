---
semantic_key: assolst__descript
title: Descript (ASSOLST)
display_names:
- DESCRIPT
kind: text
tables:
- ref: db2:assolst
  column: DESCRIPT
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Mô tả
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Descript (ASSOLST)

**Semantic key:** `assolst__descript` · **Cột vật lý:** `DESCRIPT`

## Ý nghĩa nghiệp vụ

Mô tả combo / bundle — tên chương trình gộp hàng hiển thị trên ASSOLST master.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:assolst` | `DESCRIPT` | nvarchar | Mô tả |
