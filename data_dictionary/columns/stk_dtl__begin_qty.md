---
semantic_key: stk_dtl__begin_qty
title: Tồn đầu kỳ — số lượng (STK_DTL)
display_names:
- BEGIN_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: BEGIN_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tồn đầu kỳ — số lượng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tồn đầu kỳ — số lượng (STK_DTL)

**Semantic key:** `stk_dtl__begin_qty` · **Cột vật lý:** `BEGIN_QTY`

## Ý nghĩa nghiệp vụ

Tồn kho đầu kỳ theo số lượng trên STK_DTL — snapshot trước các phát sinh nhập/xuất/bán/điều chuyển trong kỳ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `BEGIN_QTY` | numeric | Tồn đầu kỳ — số lượng |

## Ghi chú thêm

- Tồn đầu kỳ — số lượng
