---
semantic_key: customer__block_code
title: customer · block code
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BLOCK_CODE
- 'db2:customer.BLOCK_CODE: top=0(3)'
---

# customer · block code

**Semantic key:** `customer__block_code` · **Cột vật lý:** `BLOCK_CODE`

## Ý nghĩa nghiệp vụ

MãBLOCK_CODE

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `BLOCK_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

