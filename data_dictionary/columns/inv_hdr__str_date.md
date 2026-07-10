---
semantic_key: inv_hdr__str_date
title: Ngày str (INV_HDR)
display_names:
- STR_DATE
kind: date
tables:
- ref: db2:inv_hdr
  column: STR_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàySTR_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày str (INV_HDR)

**Semantic key:** `inv_hdr__str_date` · **Cột vật lý:** `STR_DATE`

## Ý nghĩa nghiệp vụ

Ngày chứng từ bán lẻ tham chiếu trên header nhập.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_hdr` | `STR_DATE` | datetime | NgàySTR_DATE |

## Ghi chú thêm

- NgàySTR_DATE
