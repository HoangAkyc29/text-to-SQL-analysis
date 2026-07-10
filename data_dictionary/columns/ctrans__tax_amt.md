---
semantic_key: ctrans__tax_amt
title: Số tiền thuế (CTRANS)
display_names:
- TAX_AMT
kind: measure
tables:
- ref: db2:ctrans
  column: TAX_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnTAX_AMT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền thuế (CTRANS)

**Semantic key:** `ctrans__tax_amt` · **Cột vật lý:** `TAX_AMT`

## Ý nghĩa nghiệp vụ

Số tiền thuế trên dòng chứng từ kế toán CTRANS — grain dòng chứng từ, join TRANS_NUM với header.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `TAX_AMT` | numeric | Số tiềnTAX_AMT |

## Ghi chú thêm

- Số tiềnTAX_AMT
