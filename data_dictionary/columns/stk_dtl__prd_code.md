---
semantic_key: stk_dtl__prd_code
title: Mã phân loại prd (STK_DTL)
display_names:
- PRD_CODE
kind: code
tables:
- ref: db2:stk_dtl
  column: PRD_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã kỳ tồn kho
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã phân loại prd (STK_DTL)

**Semantic key:** `stk_dtl__prd_code` · **Cột vật lý:** `PRD_CODE`

## Ý nghĩa nghiệp vụ

Mã kỳ báo cáo tồn kho — xác định chu kỳ (tháng/tuần) của bản ghi STK_DTL.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `PRD_CODE` | varchar | Mã kỳ tồn kho |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã kỳ tồn kho
