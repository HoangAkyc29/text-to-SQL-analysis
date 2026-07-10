---
semantic_key: inv_vatamt
title: Tiền thuế GTGT trên hóa đơn (INV_VATAMT)
display_names:
- INV_VATAMT
kind: measure
tables:
- ref: db1:strans
  column: INV_VATAMT
  type: numeric
- ref: db2:debt
  column: INV_VATAMT
  type: numeric
- ref: db2:strans
  column: INV_VATAMT
  type: numeric
- ref: db2:strans_tmp
  column: INV_VATAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- VAT trên hóa đơn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tiền thuế GTGT trên hóa đơn (INV_VATAMT)

**Semantic key:** `inv_vatamt` · **Cột vật lý:** `INV_VATAMT`

## Ý nghĩa nghiệp vụ

VAT trên hóa đơn. Dùng trong POS bán lẻ (STRANS, STRANS_TMP).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `INV_VATAMT` | numeric | VAT trên hóa đơn |
| `db2:debt` | `INV_VATAMT` | numeric | VAT trên hóa đơn |
| `db2:strans` | `INV_VATAMT` | numeric | VAT trên hóa đơn |
| `db2:strans_tmp` | `INV_VATAMT` | numeric | VAT trên hóa đơn |
