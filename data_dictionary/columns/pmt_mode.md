---
semantic_key: pmt_mode
title: pmt mode
display_names:
- PMT_MODE
kind: text
tables:
- ref: db1:strans
  column: PMT_MODE
  type: char
- ref: db1:transhdr_arc
  column: PMT_MODE
  type: char
- ref: db2:strans
  column: PMT_MODE
  type: char
- ref: db2:strans_tmp
  column: PMT_MODE
  type: char
- ref: db2:transhdr
  column: PMT_MODE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Chế độ thanh toán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# pmt mode

**Semantic key:** `pmt_mode` · **Cột vật lý:** `PMT_MODE`

## Ý nghĩa nghiệp vụ

Chế độ thanh toán (trả ngay / trả góp / công nợ, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `PMT_MODE` | char | Chế độ thanh toán |
| `db1:transhdr_arc` | `PMT_MODE` | char | Chế độ thanh toán |
| `db2:strans` | `PMT_MODE` | char | Chế độ thanh toán |
| `db2:strans_tmp` | `PMT_MODE` | char | Chế độ thanh toán |
| `db2:transhdr` | `PMT_MODE` | char | Chế độ thanh toán |
