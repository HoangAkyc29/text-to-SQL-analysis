---
semantic_key: address
title: Địa chỉ liên hệ (ADDRESS)
display_names:
- ADDRESS
- Address
kind: text
tables:
- ref: db2:cscard
  column: ADDRESS
  type: nvarchar
- ref: db2:customer
  column: ADDRESS
  type: nvarchar
- ref: db2:custsumm
  column: Address
  type: nvarchar
- ref: db2:partner
  column: ADDRESS
  type: nvarchar
- ref: db2:supplier
  column: ADDRESS
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Địa chỉ liên hệ (ADDRESS)

**Semantic key:** `address` · **Cột vật lý:** `ADDRESS`, `Address`

## Ý nghĩa nghiệp vụ

Địa chỉ liên hệ khách / đối tác — trên CUSTOMER/CSCARD là master; trên chứng từ kho có thể là địa chỉ giao nhận in trên phiếu.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `ADDRESS` | nvarchar | Địa chỉ liên hệ trên master thẻ khách hàng thân thiết |
| `db2:customer` | `ADDRESS` | nvarchar | Địa chỉ liên hệ trên danh mục master khách hàng |
| `db2:custsumm` | `Address` | nvarchar | Địa chỉ liên hệ trên bảng custsumm |
| `db2:partner` | `ADDRESS` | nvarchar | Địa chỉ liên hệ trên đối tác / khách B2B |
| `db2:supplier` | `ADDRESS` | nvarchar | Địa chỉ liên hệ trên master nhà cung cấp |
