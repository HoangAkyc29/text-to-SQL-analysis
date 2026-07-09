---
semantic_key: supplier__supp_code
title: supplier · supp code
display_names:
- SUPP_CODE
kind: code
tables:
- ref: db2:supplier
  column: SUPP_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã NCC hiển thị
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SUPP_CODE
- 'db2:supplier.SUPP_CODE: top=50694(2), 50204(1), 50760(1), 00714(1), 60144(1)'
---

# supplier · supp code

**Semantic key:** `supplier__supp_code` · **Cột vật lý:** `SUPP_CODE`

## Ý nghĩa nghiệp vụ

Cột SUPP_CODE trên SUPPLIER. db2:supplier: top 00004, 00006, 00010.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `SUPP_CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.SUPP_CODE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã NCC hiển thị
