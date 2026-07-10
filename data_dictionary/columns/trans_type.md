---
semantic_key: trans_type
title: Kiểu giao dịch chi tiết hơn TRANS_CODE (TRANS_TYPE)
display_names:
- TRANS_TYPE
kind: text
tables:
- ref: db1:crdtrans_arc
  column: TRANS_TYPE
  type: char
- ref: db2:crdtrans
  column: TRANS_TYPE
  type: char
- ref: db2:crdtrans_tmp
  column: TRANS_TYPE
  type: char
- ref: db2:ctrans
  column: TRANS_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Phân loại giao dịch thẻ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Kiểu giao dịch chi tiết hơn TRANS_CODE (TRANS_TYPE)

**Semantic key:** `trans_type` · **Cột vật lý:** `TRANS_TYPE`

## Ý nghĩa nghiệp vụ

Phân loại chi tiết loại giao dịch — bổ sung cho TRANS_CODE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `TRANS_TYPE` | char | Phân loại giao dịch thẻ |
| `db2:crdtrans` | `TRANS_TYPE` | char | Phân loại giao dịch thẻ |
| `db2:crdtrans_tmp` | `TRANS_TYPE` | char | Phân loại giao dịch thẻ |
| `db2:ctrans` | `TRANS_TYPE` | char | Phân loại giao dịch thẻ |

## Ghi chú thêm

- Phân loại giao dịch thẻ
