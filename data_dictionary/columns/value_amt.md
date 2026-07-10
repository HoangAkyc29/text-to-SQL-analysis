---
semantic_key: value_amt
title: value amt
display_names:
- VALUE_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: VALUE_AMT
  type: numeric
- ref: db2:pmcrdiss
  column: VALUE_AMT
  type: numeric
- ref: db2:pmcrdrcv
  column: VALUE_AMT
  type: numeric
- ref: db2:pmcrdstk
  column: VALUE_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Mệnh giá / giá trị thẻ PM
sources:
- table_md
- column_semantic_registry
- business_prose
---

# value amt

**Semantic key:** `value_amt` · **Cột vật lý:** `VALUE_AMT`

## Ý nghĩa nghiệp vụ

Mệnh giá / giá trị thẻ PM. Dùng trong master thẻ PM / voucher, bảng PMCRDISS, bảng PMCRDRCV, ….

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `VALUE_AMT` | numeric | Mệnh giá / giá trị thẻ PM |
| `db2:pmcrdiss` | `VALUE_AMT` | numeric | Mệnh giá / giá trị thẻ PM |
| `db2:pmcrdrcv` | `VALUE_AMT` | numeric | Mệnh giá / giá trị thẻ PM |
| `db2:pmcrdstk` | `VALUE_AMT` | numeric | Mệnh giá / giá trị thẻ PM |
