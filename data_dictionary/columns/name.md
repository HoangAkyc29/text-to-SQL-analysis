---
semantic_key: name
title: name
display_names:
- Name
- NAME
kind: text
tables:
- ref: db2:account
  column: NAME
  type: nvarchar
- ref: db2:cscard
  column: NAME
  type: nvarchar
- ref: db2:custsumm
  column: Name
  type: nvarchar
- ref: db2:partner
  column: NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên chủ thẻ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:account.NAME: top=BÕp(2), Cty TNHH Hoµng NhËt Ph­¬ng(2), B¶o H­ng Fruits(2),
  C«ng Ty TNHH Lª ThÞ(2), Cty TNHH ThÞnh TÝn §¹t(2)'
- 'db2:cscard.NAME: top=Huúnh ThÞ Kim Loan(3), Ph¹m ThÞ Thu(2), NguyÔn ThÞ Trang(2),
  TrÇn ThÞ DiÖu HiÒn(2), NguyÔn ThÞ Thanh Ch©u(2)'
- 'db2:custsumm.Name: top=Nguyễn Thị Thanh Tâm(3), Nguyễn Thị Phương(3), Trương Thị
  Mỹ Hạnh E3087(2), Nguyễn Thị Thùy Vân(2), Nguyễn Thị Tâm(2)'
- 'db2:partner.NAME: top=Cty TNHH MTV TrÞnh HiÒn(2), Cty TNHH H¶i §¶o Lý S¬n(2), Joly
  Mart(2), B¶o H­ng Fruits(2), Cty TNHH Thµnh Nh©n(2)'
---

# name

**Semantic key:** `name` · **Cột vật lý:** `Name`, `NAME`

## Ý nghĩa nghiệp vụ

Cột NAME trên ACCOUNT, CSCARD, CUSTSUMM. db2:account: top C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t, C«ng ty TNHH An Ti, C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc; db2:cscard: top Nguyen Hong S¬n, nguyeen van a, NguyÔn V¨n §¹i F2; db2:custsumm: top Lê Thị Xuân, Trần Thị Thanh Tâm, Ngô Thị Lê; db2:partner: top C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t, C«ng ty TNHH An Ti, C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `NAME` | nvarchar | có dữ liệu |
| `db2:cscard` | `NAME` | nvarchar | có dữ liệu |
| `db2:custsumm` | `Name` | nvarchar | có dữ liệu |
| `db2:partner` | `NAME` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.NAME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t`×1, `C«ng ty TNHH An Ti`×1, `C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc`×1, `C«ng ty TNHH n«ng l©m s¶n T©n Th¸i`×1, `C«ng ty TNHH Ch©u ¢u ViÖt Nam`×1, `C«ng ty d­îc §µ N½ng`×1, `C¬ së H­¬ng Nam`×1, `C«ng ty TNHH chÕ biÕn LTTP V¹n H­¬ng`×1

### `db2:cscard.NAME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Nguyen Hong S¬n`×1, `nguyeen van a`×1, `NguyÔn V¨n §¹i F2`×1, `TrÇn thÞ LÖ Ph­íc E253`×1, `NguyÔn ThÞ Thanh V©n`×1, `Lª ThÞ BÝch Xu©n`×1, `NguyÔn ThÞ Mü Thanh`×1, `TrÇn t Thanh T©m`×1

### `db2:custsumm.Name`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Lê Thị Xuân`×1, `Trần Thị Thanh Tâm`×1, `Ngô Thị Lê`×1, `Nguyễn Hoàng Yến Nhi`×1, `Nguyễn Lê Vi`×1, `Nguyễn Thị Thúy Vân.`×1, `Tôn Nữ ý Minh`×1, `Ngô Thị Kim Yến`×1

### `db2:partner.NAME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t`×1, `C«ng ty TNHH An Ti`×1, `C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc`×1, `C«ng ty TNHH n«ng l©m s¶n T©n Th¸i`×1, `C«ng ty TNHH Ch©u ¢u ViÖt Nam`×1, `C«ng ty d­îc §µ N½ng`×1, `C¬ së H­¬ng Nam`×1, `C«ng ty TNHH chÕ biÕn LTTP V¹n H­¬ng`×1

## Ghi chú thêm

- Tên chủ thẻ
