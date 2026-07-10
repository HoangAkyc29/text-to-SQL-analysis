---
semantic_key: stk_dtl__begin_amt
title: Tồn đầu kỳ — giá trị (STK_DTL)
display_names:
- BEGIN_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: BEGIN_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tồn đầu kỳ — giá trị
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tồn đầu kỳ — giá trị (STK_DTL)

**Semantic key:** `stk_dtl__begin_amt` · **Cột vật lý:** `BEGIN_AMT`

## Ý nghĩa nghiệp vụ

Tồn kho đầu kỳ theo giá trị (tiền) trên STK_DTL — dùng cùng BEGIN_QTY để đối chiếu qty × giá vốn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `BEGIN_AMT` | numeric | Tồn đầu kỳ — giá trị |

## Ghi chú thêm

- Tồn đầu kỳ — giá trị
