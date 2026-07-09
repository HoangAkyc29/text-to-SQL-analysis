---
semantic_key: address
title: address
display_names:
- Address
- ADDRESS
kind: text
tables:
- ref: db2:cscard
  column: ADDRESS
  type: nvarchar
- ref: db2:customer
  column: ADDRESS
  type: nvarchar
- ref: db2:custsumm
  column: Address
  type: nvarchar
- ref: db2:partner
  column: ADDRESS
  type: nvarchar
- ref: db2:supplier
  column: ADDRESS
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột Address
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.ADDRESS: top=§µ N½ng(25), ®n(7), 02 pasteur(6), ®µ n½ng(6), S¬n Trµ(5)'
- 'db2:customer.ADDRESS: top=§µ N½ng(13), §N(6), 02 pasteur(6), ®µ n½ng(4), ®n(3)'
- 'db2:custsumm.Address: top=đà nẵng(8), đn(7), ĐN(6), Đà Nẵng(4), 90 Nguyễn Chí Thanh(3)'
- 'db2:partner.ADDRESS: top=HCM(11), Hµ Néi(6), Tp HCM(3), §N(3), §µ N½ng(2)'
- 'db2:supplier.ADDRESS: top=HCM(12), Hµ Néi(7), Tp HCM(2), §N(2), §µ N½ng(2)'
---

# address

**Semantic key:** `address` · **Cột vật lý:** `Address`, `ADDRESS`

## Ý nghĩa nghiệp vụ

Cột ADDRESS trên CSCARD, CUSTOMER, CUSTSUMM. db2:cscard: top Daisy, dasdasd, 105 TrÇn Phó; db2:customer: top NVSThi, NHVCB, K152/15 Lý Tù Träng; db2:custsumm: top 14 Phan Đình Phùng, 341 Ông ích Khiêm, 317 Nguyễn Hoàng; db2:partner: top 27A B×nh Phó, P10, Q6, TP HCM, 01 QL1, Xu©n T©n, Long Kh¸nh, §Nai, B3d, Khu B, KCN HiÖp Ph­íc, Nhµ BÌ, TPHCM; db2:supplier: top 27A B×nh Phó, P10, Q6, TP HCM, 01 QL1, Xu©n T©n, Long Kh¸nh, §Nai, B3d, Khu B, KCN HiÖp Ph­íc, Nhµ BÌ, TPHCM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `ADDRESS` | nvarchar | có dữ liệu |
| `db2:customer` | `ADDRESS` | nvarchar | có dữ liệu |
| `db2:custsumm` | `Address` | nvarchar | có dữ liệu |
| `db2:partner` | `ADDRESS` | nvarchar | có dữ liệu |
| `db2:supplier` | `ADDRESS` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.ADDRESS`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Daisy`×1, `dasdasd`×1, `105 TrÇn Phó`×1, `168A BÕ V¨n §µn`×1, `15 Lý Th­êng KiÖt`×1, `198/34 Quang Trung`×1, `267A §èng §a`×1, `76 Lª DuÈn`×1

### `db2:customer.ADDRESS`
- Null rate trong sample: 0%
- Distinct ≈19; top: `NVSThi`×2, `NHVCB`×1, `K152/15 Lý Tù Träng`×1, `K34 Lª DuÈn`×1, `105 TrÇn Phó`×1, `NV siªu thÞ`×1, `79 hoµng DiÖu`×1, `L« 46 D1 L­u H÷u Ph­íc`×1

### `db2:custsumm.Address`
- Null rate trong sample: 0%
- Distinct ≈20; top: `14 Phan Đình Phùng`×1, `341 Ông ích Khiêm`×1, `317 Nguyễn Hoàng`×1, `149 Lê Lợi`×1, `90/12 Trần Phú _ Hải châu`×1, `Chung cư 4a Nại Hiên Đông`×1, `K10/9 Phạm Văn Nghị`×1, `Hòa Châu Hòa Vang`×1

### `db2:partner.ADDRESS`
- Null rate trong sample: 60%
- Distinct ≈8; top: `27A B×nh Phó, P10, Q6, TP HCM`×1, `01 QL1, Xu©n T©n, Long Kh¸nh, §Nai`×1, `B3d, Khu B, KCN HiÖp Ph­íc, Nhµ BÌ, TPHCM`×1, `173/15 Ph¹m Phó Thø- P11- Q.T©n B×nh`×1, `K15/08 §µo Duy Tõ -TP §µ N½ng`×1, `K132/2 Huúnh Ngäc HuÖ-§µ N½ng`×1, `X· Long Phuíc-HuyÖn Long Thµnh-TØnh §ång Nai`×1, `334/10 - 12 Minh Phông, P12-Q11`×1

### `db2:supplier.ADDRESS`
- Null rate trong sample: 60%
- Distinct ≈8; top: `27A B×nh Phó, P10, Q6, TP HCM`×1, `01 QL1, Xu©n T©n, Long Kh¸nh, §Nai`×1, `B3d, Khu B, KCN HiÖp Ph­íc, Nhµ BÌ, TPHCM`×1, `173/15 Ph¹m Phó Thø- P11- Q.T©n B×nh`×1, `K15/08 §µo Duy Tõ -TP §µ N½ng`×1, `K132/2 Huúnh Ngäc HuÖ-§µ N½ng`×1, `X· Long Phuíc-HuyÖn Long Thµnh-TØnh §ång Nai`×1, `334/10 - 12 Minh Phông, P12-Q11`×1

## Ghi chú thêm

- Cột Address
