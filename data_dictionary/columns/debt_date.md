---
semantic_key: debt_date
title: Ngày phát sinh công nợ (DEBT_DATE)
display_names:
- DEBT_DATE
kind: date
tables:
- ref: db2:ctrans
  column: DEBT_DATE
  type: datetime
- ref: db2:debt
  column: DEBT_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày phát sinh công nợ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày phát sinh công nợ (DEBT_DATE)

**Semantic key:** `debt_date` · **Cột vật lý:** `DEBT_DATE`

## Ý nghĩa nghiệp vụ

Ngày phát sinh công nợ trên chứng từ DEBT / CTRANS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `DEBT_DATE` | datetime | Ngày phát sinh công nợ |
| `db2:debt` | `DEBT_DATE` | datetime | Ngày phát sinh công nợ |
