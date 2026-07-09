---
semantic_key: remark
title: remark
display_names:
- REMARK
- Remark
kind: text
tables:
- ref: db1:pmtrans
  column: REMARK
  type: nvarchar
- ref: db1:strans
  column: REMARK
  type: nvarchar
- ref: db1:transhdr_arc
  column: REMARK
  type: nvarchar
- ref: db2:cscard
  column: REMARK
  type: nvarchar
- ref: db2:ctrans
  column: REMARK
  type: nvarchar
- ref: db2:customer
  column: REMARK
  type: nvarchar
- ref: db2:custsumm
  column: Remark
  type: nvarchar
- ref: db2:debt
  column: REMARK
  type: nvarchar
- ref: db2:inv_iss
  column: REMARK
  type: nvarchar
- ref: db2:partner
  column: REMARK
  type: nvarchar
- ref: db2:pmcrdiss
  column: REMARK
  type: nvarchar
- ref: db2:pmcrdstk
  column: REMARK
  type: nvarchar
- ref: db2:pmtrans
  column: REMARK
  type: nvarchar
- ref: db2:st_order
  column: REMARK
  type: nvarchar
- ref: db2:strans
  column: REMARK
  type: nvarchar
- ref: db2:supplier
  column: REMARK
  type: nvarchar
- ref: db2:transhdr
  column: REMARK
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Ghi chú nghiệp vụ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.REMARK: top=C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0(6)'
- 'db1:strans.REMARK: top=CÊn ®èi tù ®éng hµng tån ©m vÒ 0(62), CÊn ®èi tù ®éng hµng
  tån ©m kú tr­íc chuyÓn sang kú nµy(55), Can doi dieu chinh gia von(26), 24.4.25(3),
  PHUNG === LY 28/4/25(2)'
- 'db1:transhdr_arc.REMARK: top=c® m·(1), 4.9.23(1), Nh theo H§20788 04/10/19(1),
  11.3-p(1), lý xuÊt phïng 28/12/25(1)'
- 'db2:cscard.REMARK: top=42(06/11/13)  62(10/01/14)(1), nh©n viªn siªu thÞ(1), tõ
  thÎ 13152(1), ®æi thÎ E3174 ngµy 24/9/23(1), 30(23/1/16) cÊp l¹i 1(1)'
- 'db2:ctrans.REMARK: top=29.6.26(10), 11.6.26(7), 15.6-p(7), 15.6.26(6), 2.6.26(6)'
- 'db2:customer.REMARK: top=64(16/11/13)(1), 50 100(23/2/17) §æi thÎ 3/9/19(1), 94(21/6/15)
  100(16/1/16)(1), 250(31/3/17)(1), 30,60(29/09/2014)(1)'
- 'db2:custsumm.Remark: top=250(28/3/17)(2), 105(25/07/2014)(1), 100(12/10/14) 177(8/2/15)(1),
  37(13/9/14)(1), A51764 - A43072(1)'
- 'db2:debt.REMARK: top=c® m·(13), m· gg(5), cs m· gg(3), BBNH ngµy 25/2/18(2), chuyÓn
  m· hµng b¸n(2)'
- 'db2:inv_iss.REMARK: top=m_EInvoice = 0 _InvOption = 3.2(119), m_EInvoice = 5 Option3.2(8)'
- 'db2:partner.REMARK: top=Chuyªn cung cÊp b¸nh kÑo c¸c lo¹i(2), Chuyªn cung cÊp trµ
  c¸c lo¹i(2), Chuyªn cung cÊp TP ®«ng l¹nh(1), Cung cÊp b¸nh kÑo c¸c lo¹i(1), Chuyªn
  cung cÊp s¶n phÈm Kinh §«(1)'
- 'db2:pmcrdiss.REMARK: top=BVDL(99), bv nhi(67), bv h¶i ch©u(49), VCB(38), hai quan(35)'
- 'db2:pmcrdstk.REMARK: top=BVDL(118), bv nhi(63), bv h¶i ch©u(46), VCB(42), hai quan(32)'
- 'db2:pmtrans.REMARK: top=C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0(8)'
- 'db2:st_order.REMARK: top=phung==> nghi 21/6/26(77), phung==> ly 21/6/26(49), phung==>
  nghi 4/6/26(37), phung==> ly 23/6/26(33), phung == nghi 17/06/26(30)'
- 'db2:strans.REMARK: top=CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy(61),
  9.6l(3), 26.6p(2), huy-n(2), 22.6.26(2)'
- 'db2:supplier.REMARK: top=Chuyªn cung cÊp b¸nh kÑo c¸c lo¹i(3), Chuyªn cung cÊp
  thùc phÈm(2), Chuyªn cung cÊp ho¸ mü phÈm(2), Chuyªn cung cÊp thùc phÈm ®«ng l¹nh(1),
  Chuyªn cung cÊp gèm sø c¸c lo¹i(1)'
- 'db2:transhdr.REMARK: top=H§203 22/6(1), LTN H§21393 03/6(1), 13.6-p(1), 10.6-l(1),
  hñy bb 19.6.26(1)'
---

# remark

**Semantic key:** `remark` · **Cột vật lý:** `REMARK`, `Remark`

## Ý nghĩa nghiệp vụ

Cột REMARK trên CSCARD, CTRANS, CUSTOMER. db1:pmtrans: sample toàn rỗng; db1:strans: vd. «01/4»; db1:transhdr_arc: sample toàn rỗng; db2:cscard: vd. «CÊp ph¸t tù ®éng»; db2:ctrans: vd. «2.6.26»; db2:customer: vd. «Vip 3.5»; db2:custsumm: vd. «E1845 rớt»; db2:debt: vd. «hd1322-28/11/2012»; db2:inv_iss: sample toàn rỗng; db2:partner: vd. «Chuyªn cung cÊp ho¸ mü phÈm»; db2:pmcrdiss: vd. «bv h¶i ch©u»; db2:pmcrdstk: vd. «ThÎ XuÊt tÆng KH nh©n khai tr­¬ng»; db2:pmtrans: vd. «C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0»; db2:st_order: vd. «K-N 1.6.26»; db2:strans: vd. «LTN 01/6»; db2:supplier: vd. «Chuyªn cung cÊp ho¸ mü phÈm»; db2:transhdr: vd. «1.6.26».

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `REMARK` | nvarchar | có dữ liệu |
| `db1:strans` | `REMARK` | nvarchar | có dữ liệu |
| `db1:transhdr_arc` | `REMARK` | nvarchar | có dữ liệu |
| `db2:cscard` | `REMARK` | nvarchar | có dữ liệu |
| `db2:ctrans` | `REMARK` | nvarchar | có dữ liệu |
| `db2:customer` | `REMARK` | nvarchar | có dữ liệu |
| `db2:custsumm` | `Remark` | nvarchar | có dữ liệu |
| `db2:debt` | `REMARK` | nvarchar | có dữ liệu |
| `db2:inv_iss` | `REMARK` | nvarchar | có dữ liệu |
| `db2:partner` | `REMARK` | nvarchar | có dữ liệu |
| `db2:pmcrdiss` | `REMARK` | nvarchar | có dữ liệu |
| `db2:pmcrdstk` | `REMARK` | nvarchar | có dữ liệu |
| `db2:pmtrans` | `REMARK` | nvarchar | có dữ liệu |
| `db2:st_order` | `REMARK` | nvarchar | có dữ liệu |
| `db2:strans` | `REMARK` | nvarchar | có dữ liệu |
| `db2:supplier` | `REMARK` | nvarchar | có dữ liệu |
| `db2:transhdr` | `REMARK` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.REMARK`
- Null rate trong sample: 0%
- Distinct ≈3; top: `01/4`×10, `1.4.26`×5, `10.4.26`×5

### `db2:cscard.REMARK`
- Null rate trong sample: 10%
- Distinct ≈17; top: `CÊp ph¸t tù ®éng`×2, `doi vip F2`×1, `76-gi h¹n 3t-chuyÓn sang E253`×1, `chuyen sang e308t`×1, `doi the vip moi 128`×1, `huû chuyÔn sang E222`×1, `gia h¹n 3t- huû chuyÓn sang E273`×1, `gia h¹n 3t`×1

### `db2:ctrans.REMARK`
- Null rate trong sample: 0%
- Distinct ≈14; top: `2.6.26`×4, `1.6.26`×3, `LTN 01/6`×2, `tam`×1, `h® 61-2.6.26`×1, `hd 155-1.6.26`×1, `h® 172-2.6.26`×1, `h® 167-2.6.26`×1

### `db2:customer.REMARK`
- Null rate trong sample: 10%
- Distinct ≈15; top: `Vip 3.5`×4, `ThÎ ®Æt c¸ch theo ®Ò nghÞ G.®èc S.thÞ`×1, `+3  Vip 3%`×1, `dcach nhan vien`×1, `Dcach nhan vien`×1, `vp 3%`×1, `p60 18/5  P40 26/6`×1, `(+3d sua) doi the E341`×1

### `db2:custsumm.Remark`
- Null rate trong sample: 85%
- Distinct ≈3; top: `E1845 rớt`×1, `Đổi Thẻ 2694 ngày 09/02/2022`×1, `Đổi thẻ 25/8/19`×1

### `db2:debt.REMARK`
- Null rate trong sample: 0%
- Distinct ≈20; top: `hd1322-28/11/2012`×1, `hd1321-28/11-2012`×1, `NK theo H§0000133 ngµy 24/12/12`×1, `hd1320-28/11/2012`×1, `hd1319-28/11/2012`×1, `hd1318-28-12-2012`×1, `H§ nhËp 3011 ngµy 26/11/2012`×1, `H§ nhËp 3012 ngµy 26/11/2012`×1

### `db2:partner.REMARK`
- Null rate trong sample: 50%
- Distinct ≈9; top: `Chuyªn cung cÊp ho¸ mü phÈm`×2, `Chuyªn cung cÊp thùc phÈm kh«`×1, `Chuyªn cung cÊp mü phÈm`×1, `Chuyªn cung cÊp ho¸ mü phÈm, ®å gia vÞ`×1, `Chuyªn cung cÊp thùc phÈm, ®å hép ¨n liÒn`×1, `Chuyªn cung cÊp c¸c chÊy tÈy röa`×1, `Chuyªn cung cÊp b¸nh kÑo c¸c lo¹i`×1, `Chuyªn cung cÊp ®å gia dông`×1

### `db2:pmcrdiss.REMARK`
- Null rate trong sample: 0%
- Distinct ≈2; top: `bv h¶i ch©u`×19, `BV h¶i ch©u`×1

### `db2:pmcrdstk.REMARK`
- Null rate trong sample: 0%
- Distinct ≈4; top: `ThÎ XuÊt tÆng KH nh©n khai tr­¬ng`×13, `T¹o ®Ó b¸n`×5, `KhuyÕn m·i khai truong Siªu ThÞ`×1, `B¸n cho Ng©n hµng BIDV §N ch­a thu tiÒn`×1

### `db2:pmtrans.REMARK`
- Null rate trong sample: 85%
- Distinct ≈1; top: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0`×3

### `db2:st_order.REMARK`
- Null rate trong sample: 0%
- Distinct ≈2; top: `K-N 1.6.26`×17, `phung==> ly 2/6/26`×3

### `db2:strans.REMARK`
- Null rate trong sample: 0%
- Distinct ≈3; top: `LTN 01/6`×15, `1.6.26`×4, `tam`×1

### `db2:supplier.REMARK`
- Null rate trong sample: 50%
- Distinct ≈9; top: `Chuyªn cung cÊp ho¸ mü phÈm`×2, `Chuyªn cung cÊp thùc phÈm kh«`×1, `Chuyªn cung cÊp mü phÈm`×1, `Chuyªn cung cÊp ho¸ mü phÈm, ®å gia vÞ`×1, `Chuyªn cung cÊp thùc phÈm, ®å hép ¨n liÒn`×1, `Chuyªn cung cÊp c¸c chÊy tÈy röa`×1, `Chuyªn cung cÊp b¸nh kÑo c¸c lo¹i`×1, `Chuyªn cung cÊp ®å gia dông`×1

### `db2:transhdr.REMARK`
- Null rate trong sample: 0%
- Distinct ≈15; top: `1.6.26`×3, `LTN 01/6`×2, `KM LDL 02/6`×2, `KM LTN 02/6`×2, `tam`×1, `h® 61-2.6.26`×1, `KM PDP 02/6`×1, `2.6.26`×1

## Ghi chú thêm

- Ghi chú nghiệp vụ
