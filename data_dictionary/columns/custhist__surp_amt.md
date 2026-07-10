---
semantic_key: custhist__surp_amt
title: Số tiền / giá trị (CUSTHIST)
display_names:
- SURP_AMT
kind: measure
tables:
- ref: db2:custhist
  column: SURP_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnSURP_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (CUSTHIST)

**Semantic key:** `custhist__surp_amt` · **Cột vật lý:** `SURP_AMT`

## Ý nghĩa nghiệp vụ

Số tiền / giá trị — lịch sử thay đổi thông tin khách.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:custhist` | `SURP_AMT` | numeric | Số tiềnSURP_AMT |

## Ghi chú thêm

- Số tiềnSURP_AMT
