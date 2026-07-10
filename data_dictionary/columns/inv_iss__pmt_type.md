---
semantic_key: inv_iss__pmt_type
title: Pmt Type (INV_ISS)
display_names:
- PMT_TYPE
kind: text
tables:
- ref: db2:inv_iss
  column: PMT_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại thanh toán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Pmt Type (INV_ISS)

**Semantic key:** `inv_iss__pmt_type` · **Cột vật lý:** `PMT_TYPE`

## Ý nghĩa nghiệp vụ

Thuộc tính pmt type — phiếu xuất kho.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `PMT_TYPE` | char | Loại thanh toán |

## Ghi chú thêm

- Loại thanh toán
