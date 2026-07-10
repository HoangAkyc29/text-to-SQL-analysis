---
semantic_key: pmcrdinf__stk_date
title: Ngày stk (PMCRDINF)
display_names:
- STK_DATE
kind: date
tables:
- ref: db2:pmcrdinf
  column: STK_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàySTK_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày stk (PMCRDINF)

**Semantic key:** `pmcrdinf__stk_date` · **Cột vật lý:** `STK_DATE`

## Ý nghĩa nghiệp vụ

Ngày nhập kho batch voucher PM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `STK_DATE` | datetime | NgàySTK_DATE |

## Ghi chú thêm

- NgàySTK_DATE
