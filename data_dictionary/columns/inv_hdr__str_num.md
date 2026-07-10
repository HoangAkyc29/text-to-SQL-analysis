---
semantic_key: inv_hdr__str_num
title: Mã định danh (str num) (INV_HDR)
display_names:
- STR_NUM
kind: identifier
tables:
- ref: db2:inv_hdr
  column: STR_NUM
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (str num) (INV_HDR)

**Semantic key:** `inv_hdr__str_num` · **Cột vật lý:** `STR_NUM`

## Ý nghĩa nghiệp vụ

Số chứng từ bán lẻ tham chiếu khi nhập hàng trả / đối soát.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_hdr` | `STR_NUM` | char | Mã định danh (str num) trên header hóa đơn mua / nhập |
