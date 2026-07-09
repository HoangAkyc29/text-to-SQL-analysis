---
semantic_key: inv_type
title: inv type
display_names:
- INV_TYPE
kind: text
tables:
- ref: db1:strans
  column: INV_TYPE
  type: varchar
- ref: db2:debt
  column: INV_TYPE
  type: varchar
- ref: db2:inv_hdr
  column: INV_TYPE
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Loại hóa đơn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.INV_TYPE: top=1(31)'
- 'db2:debt.INV_TYPE: top=1(254), 0(1), 806(1)'
- 'db2:inv_hdr.INV_TYPE: top=1(754), 1747(1)'
---

# inv type

**Semantic key:** `inv_type` · **Cột vật lý:** `INV_TYPE`

## Ý nghĩa nghiệp vụ

Loại hóa đơn

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `INV_TYPE` | varchar | có dữ liệu |
| `db2:debt` | `INV_TYPE` | varchar | có dữ liệu |
| `db2:inv_hdr` | `INV_TYPE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

