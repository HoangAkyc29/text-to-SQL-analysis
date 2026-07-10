---
semantic_key: supplier__pmt_seq
title: Pmt Seq (SUPPLIER)
display_names:
- PMT_SEQ
kind: text
tables:
- ref: db2:supplier
  column: PMT_SEQ
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Pmt Seq (SUPPLIER)

**Semantic key:** `supplier__pmt_seq` · **Cột vật lý:** `PMT_SEQ`

## Ý nghĩa nghiệp vụ

Thứ tự / điều khoản thanh toán mặc định với NCC (công nợ, COD, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `PMT_SEQ` | char | Thuộc tính pmt seq trên master nhà cung cấp |
