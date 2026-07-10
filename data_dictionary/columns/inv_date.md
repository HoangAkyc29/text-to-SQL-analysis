---
semantic_key: inv_date
title: Ngày hóa đơn (INV_DATE)
display_names:
- INV_DATE
- INV_Date
kind: date
tables:
- ref: db1:strans
  column: INV_Date
  type: datetime
- ref: db2:ctrans
  column: INV_DATE
  type: datetime
- ref: db2:debt
  column: INV_Date
  type: datetime
- ref: db2:inv_hdr
  column: INV_DATE
  type: datetime
- ref: db2:inv_iss
  column: INV_DATE
  type: datetime
- ref: db2:strans
  column: INV_Date
  type: datetime
- ref: db2:strans_tmp
  column: INV_Date
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày hóa đơn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày hóa đơn (INV_DATE)

**Semantic key:** `inv_date` · **Cột vật lý:** `INV_DATE`, `INV_Date`

## Ý nghĩa nghiệp vụ

Ngày hóa đơn. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Kho / mua hàng (INV_HDR, INV_ISS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `INV_Date` | datetime | Ngày hóa đơn |
| `db2:ctrans` | `INV_DATE` | datetime | Ngày hóa đơn |
| `db2:debt` | `INV_Date` | datetime | Ngày hóa đơn |
| `db2:inv_hdr` | `INV_DATE` | datetime | Ngày hóa đơn |
| `db2:inv_iss` | `INV_DATE` | datetime | Ngày hóa đơn |
| `db2:strans` | `INV_Date` | datetime | Ngày hóa đơn |
| `db2:strans_tmp` | `INV_Date` | datetime | Ngày hóa đơn |
