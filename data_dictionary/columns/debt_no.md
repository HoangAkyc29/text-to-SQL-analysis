---
semantic_key: debt_no
title: Số chứng từ công nợ (DEBT_NO)
display_names:
- DEBT_NO
kind: identifier
tables:
- ref: db2:ctrans
  column: DEBT_NO
  type: char
- ref: db2:debt
  column: DEBT_NO
  type: char
join_with: []
related_semantic_keys: []
facts:
- Số chứng từ công nợ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số chứng từ công nợ (DEBT_NO)

**Semantic key:** `debt_no` · **Cột vật lý:** `DEBT_NO`

## Ý nghĩa nghiệp vụ

Số chứng từ công nợ — khóa join DEBT ↔ CTRANS ↔ thanh toán. Dùng tra công nợ phải thu/phải trả khách hoặc NCC.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `DEBT_NO` | char | Số chứng từ công nợ |
| `db2:debt` | `DEBT_NO` | char | Số chứng từ công nợ |
