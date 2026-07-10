---
semantic_key: asso_id
title: Mã combo / bundle (ASSO_ID)
display_names:
- ASSO_ID
kind: identifier
tables:
- ref: db1:strans
  column: ASSO_ID
  type: char
- ref: db2:asso_inf
  column: ASSO_ID
  type: char
- ref: db2:assolst
  column: ASSO_ID
  type: char
- ref: db2:strans
  column: ASSO_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã combo/bundle
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã combo / bundle (ASSO_ID)

**Semantic key:** `asso_id` · **Cột vật lý:** `ASSO_ID`

## Ý nghĩa nghiệp vụ

Mã combo / bundle — liên kết ASSOLST (header) ↔ ASSO_INF (chi tiết thành phần).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `ASSO_ID` | char | Mã combo/bundle |
| `db2:asso_inf` | `ASSO_ID` | char | Mã combo/bundle |
| `db2:assolst` | `ASSO_ID` | char | Mã combo/bundle |
| `db2:strans` | `ASSO_ID` | char | Mã combo/bundle |

## Ghi chú thêm

- Mã combo/bundle
