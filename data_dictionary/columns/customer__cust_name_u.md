---
semantic_key: customer__cust_name_u
title: customer · cust name u
display_names:
- CUST_NAME_U
kind: text
tables:
- ref: db2:customer
  column: CUST_NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột CUST_NAME_U
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CUST_NAME_U
- 'db2:customer.CUST_NAME_U: top=Nguyễn Thị Hằng(3), Nguyễn Thị Mai(2), Nguyễn Thu
  Hương(2), Nguyễn Thị Thanh Vân(2), Trương Thị Thùy Trang(2)'
---

# customer · cust name u

**Semantic key:** `customer__cust_name_u` · **Cột vật lý:** `CUST_NAME_U`

## Ý nghĩa nghiệp vụ

Cột CUST_NAME_U trên CUSTOMER. db2:customer: top Nguyễn Quốc Bình, Vương Đình Chỉnh, Vũ Minh An.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CUST_NAME_U` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.CUST_NAME_U`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Nguyễn Quốc Bình`×1, `Vương Đình Chỉnh`×1, `Vũ Minh An`×1, `Nguyễn Văn Đại`×1, `Võ Văn Thảo`×1, `Trần Lan Hương`×1, `Nguyễn Thị Khánh Dung`×1, `Trần tthị Kim Yến`×1

## Ghi chú thêm

