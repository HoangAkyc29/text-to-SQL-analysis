---
semantic_key: cust_name
title: Tên khách hàng
display_names:
- CUST_NAME
kind: text
tables:
- ref: db2:customer
  column: CUST_NAME
  type: nvarchar
- ref: db2:inv_iss
  column: CUST_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên khách hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tên khách hàng

**Semantic key:** `cust_name` · **Cột vật lý:** `CUST_NAME`

## Ý nghĩa nghiệp vụ

Tên khách hàng đã đăng ký hoặc ghi nhận trên chứng từ. Trên CUSTOMER là tên master; trên INV_ISS là tên in phiếu xuất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `CUST_NAME` | nvarchar | tên chính thức trên danh mục master khách hàng đã đăng ký |
| `db2:inv_iss` | `CUST_NAME` | nvarchar | tên khách in trên phiếu xuất — có thể lấy từ master hoặc nhập khi xuất |
