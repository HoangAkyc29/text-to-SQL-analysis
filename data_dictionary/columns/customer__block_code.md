---
semantic_key: customer__block_code
title: Mã phân loại block (CUSTOMER)
display_names:
- BLOCK_CODE
kind: code
tables:
- ref: db2:customer
  column: BLOCK_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- MãBLOCK_CODE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã phân loại block (CUSTOMER)

**Semantic key:** `customer__block_code` · **Cột vật lý:** `BLOCK_CODE`

## Ý nghĩa nghiệp vụ

Mã block / phân khối phân loại khách hoặc NCC trên master. Trên master CUSTOMER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `BLOCK_CODE` | char | MãBLOCK_CODE |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- MãBLOCK_CODE
