---
semantic_key: cust_name
title: cust name
display_names:
- CUST_NAME
kind: text
tables:
- ref: db2:customer
  column: CUST_NAME
  type: nvarchar
- ref: db2:inv_iss
  column: CUST_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên khách hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.CUST_NAME: top=NguyÔn ThÞ H»ng(3), NguyÔn ThÞ Mai(2), NguyÔn Thu H­¬ng(2),
  NguyÔn ThÞ Thanh V©n(2), Tr­¬ng ThÞ Thïy Trang(2)'
- 'db2:inv_iss.CUST_NAME: top=D­¬ng V©n Anh(20), Mai ThÞ H¹nh 3(6), Mai ThÞ Hoµi Thóy
  E3083(4), TrÇn Hßa Nh·(3), vâ trÇn thanh ph­¬ng 1(3)'
---

# cust name

**Semantic key:** `cust_name` · **Cột vật lý:** `CUST_NAME`

## Ý nghĩa nghiệp vụ

Cột CUST_NAME trên CUSTOMER, INV_ISS. db2:customer: top NguyÔn Quèc B×nh, V­¬ng §×nh ChØnh, Vò Minh An; db2:inv_iss: top NguyÔn ThÞ MËn E2733, NguyÔn TÊn MÉn, Bïi ThÞ Ph­¬ng Th¶o.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CUST_NAME` | nvarchar | có dữ liệu |
| `db2:inv_iss` | `CUST_NAME` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.CUST_NAME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `NguyÔn Quèc B×nh`×1, `V­¬ng §×nh ChØnh`×1, `Vò Minh An`×1, `NguyÔn V¨n §¹i`×1, `Vâ V¨n Th¶o`×1, `TrÇn Lan H­¬ng`×1, `NguyÔn ThÞ Kh¸nh Dung`×1, `TrÇn tthÞ Kim YÕn`×1

### `db2:inv_iss.CUST_NAME`
- Null rate trong sample: 5%
- Distinct ≈19; top: `NguyÔn ThÞ MËn E2733`×1, `NguyÔn TÊn MÉn`×1, `Bïi ThÞ Ph­¬ng Th¶o`×1, `nguyÔn minh ph­¬ng`×1, `Ph¹m ThÞ Dung`×1, `Lª Thu Hµ`×1, `NguyÔn T Tuý Loan`×1, `nguyen thi truc`×1

## Ghi chú thêm

- Tên khách hàng
