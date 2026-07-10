---
semantic_key: inv_hdr__custac
title: Custac (INV_HDR)
display_names:
- CUSTAC
kind: text
tables:
- ref: db2:inv_hdr
  column: CUSTAC
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Custac (INV_HDR)

**Semantic key:** `inv_hdr__custac` · **Cột vật lý:** `CUSTAC`

## Ý nghĩa nghiệp vụ

Tài khoản công nợ khách gắn hóa đơn mua / nhập.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_hdr` | `CUSTAC` | char | Thuộc tính custac trên header hóa đơn mua / nhập |
