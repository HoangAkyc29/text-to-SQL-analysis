---
semantic_key: pmcrdinf__stk_num
title: Mã định danh (stk num) (PMCRDINF)
display_names:
- STK_NUM
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: STK_NUM
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (stk num) (PMCRDINF)

**Semantic key:** `pmcrdinf__stk_num` · **Cột vật lý:** `STK_NUM`

## Ý nghĩa nghiệp vụ

Số phiếu nhập kho voucher PM (batch stock PM card).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `STK_NUM` | char | Mã định danh (stk num) trên master thẻ PM / voucher |
