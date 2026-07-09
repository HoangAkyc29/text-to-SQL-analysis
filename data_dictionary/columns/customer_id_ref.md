---
semantic_key: customer_id_ref
title: customer id ref
display_names:
- CUST_ID
- cust_id
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: CUST_ID
  type: char
- ref: db1:pmtrans
  column: CUST_ID
  type: char
- ref: db1:transhdr_arc
  column: CUST_ID
  type: char
- ref: db2:account
  column: CUST_ID
  type: char
- ref: db2:crd_info
  column: CUST_ID
  type: char
- ref: db2:crdtrans
  column: CUST_ID
  type: char
- ref: db2:crdtrans_tmp
  column: CUST_ID
  type: char
- ref: db2:ctrans
  column: CUST_ID
  type: char
- ref: db2:debt
  column: CUST_ID
  type: char
- ref: db2:inv_hdr
  column: CUST_ID
  type: char
- ref: db2:inv_iss
  column: CUST_ID
  type: char
- ref: db2:pmcrdinf
  column: CUST_ID
  type: char
- ref: db2:pmcrdiss
  column: CUST_ID
  type: char
- ref: db2:pmcrdrcv
  column: CUST_ID
  type: char
- ref: db2:pmcrdstk
  column: CUST_ID
  type: char
- ref: db2:pmtrans
  column: CUST_ID
  type: char
- ref: db2:rdiscinf
  column: CUST_ID
  type: char
- ref: db2:st_order
  column: CUST_ID
  type: char
- ref: db2:webrpt_rfm_snapshot
  column: cust_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã khách hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.CUST_ID: top=239010007719(3), 239020002306(2), 230000020547(2), 230000012254(2),
  239010007187(2)'
- 'db2:account.CUST_ID: top=60174(1), 00164(1), 50633(1), 51128(1), 51576(1)'
- 'db2:ctrans.CUST_ID: top=50971(62), 00062(46), 50617(45), 51508(36), 51451(34)'
- 'db2:debt.CUST_ID: top=00062(46), 50617(34), 50371(26), 50724(26), 50426(24)'
- 'db2:inv_hdr.CUST_ID: top=00062(51), 50371(42), 50648(34), 50746(28), 50701(26)'
- 'db2:inv_iss.CUST_ID: top=230000029208(20), 230000012078(6), 230000029633(4), 230000006299(3),
  230000011044(3)'
- 'db2:pmcrdinf.CUST_ID: top=230000000001(209), 230000000499(6), 230000000005(5),
  230000032762(1), 230000010382(1)'
- 'db2:pmcrdiss.CUST_ID: top=230000000001(488), 230000000005(6)'
- 'db2:pmcrdrcv.CUST_ID: top=230000030436(9), 230000016371(7), 230000031566(7), 230000005476(6),
  230000000150(5)'
- 'db2:pmcrdstk.CUST_ID: top=230000000001(505), 230000000005(10)'
- 'db2:pmtrans.CUST_ID: top=230000008763(4), 230000031769(3), 239010004478(3), 230000000025(3),
  239020002937(2)'
- 'db2:webrpt_rfm_snapshot.cust_id: top=230000031854(1), 230000021531(1), 230000007104(1),
  239010009193(1), 239020001986(1)'
---

# customer id ref

**Semantic key:** `customer_id_ref` · **Cột vật lý:** `CUST_ID`, `cust_id`

## Ý nghĩa nghiệp vụ

Cột CUST_ID trên ACCOUNT, CRDTRANS, CRDTRANS_ARC. db1:crdtrans_arc: sample toàn rỗng; db1:pmtrans: top 230000007329, 230000021576, 239010008076; db1:transhdr_arc: sample toàn rỗng; db2:account: top 00004, 00006, 00010; db2:crd_info: sample toàn rỗng; db2:crdtrans: sample toàn rỗng; db2:crdtrans_tmp: sample toàn rỗng; db2:ctrans: top 50855, 51547, 51373; db2:debt: top 00097, 00469, 00043; db2:inv_hdr: top 51436, 51345, 50361; db2:inv_iss: top 230000000001, 230000000437, 230000000468; db2:pmcrdinf: sample toàn rỗng; db2:pmcrdiss: top 230000000001; db2:pmcrdrcv: top 230000004963, 239020002189, 230000032428; db2:pmcrdstk: sample toàn rỗng; db2:pmtrans: sample toàn rỗng; db2:rdiscinf: sample toàn rỗng; db2:st_order: sample toàn rỗng; db2:webrpt_rfm_snapshot: top 230000012826, 230000000935, 239010001245.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `CUST_ID` | char | Không có giá trị trong sample |
| `db1:pmtrans` | `CUST_ID` | char | có dữ liệu |
| `db1:transhdr_arc` | `CUST_ID` | char | Không có giá trị trong sample |
| `db2:account` | `CUST_ID` | char | có dữ liệu |
| `db2:crd_info` | `CUST_ID` | char | Không có giá trị trong sample |
| `db2:crdtrans` | `CUST_ID` | char | Không có giá trị trong sample |
| `db2:crdtrans_tmp` | `CUST_ID` | char | Không có giá trị trong sample |
| `db2:ctrans` | `CUST_ID` | char | có dữ liệu |
| `db2:debt` | `CUST_ID` | char | có dữ liệu |
| `db2:inv_hdr` | `CUST_ID` | char | có dữ liệu |
| `db2:inv_iss` | `CUST_ID` | char | có dữ liệu |
| `db2:pmcrdinf` | `CUST_ID` | char | có dữ liệu |
| `db2:pmcrdiss` | `CUST_ID` | char | có dữ liệu |
| `db2:pmcrdrcv` | `CUST_ID` | char | có dữ liệu |
| `db2:pmcrdstk` | `CUST_ID` | char | có dữ liệu |
| `db2:pmtrans` | `CUST_ID` | char | có dữ liệu |
| `db2:rdiscinf` | `CUST_ID` | char | Không có giá trị trong sample |
| `db2:st_order` | `CUST_ID` | char | Không có giá trị trong sample |
| `db2:webrpt_rfm_snapshot` | `cust_id` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.CUST_ID`
- Null rate trong sample: 30%
- Distinct ≈9; top: `230000007329`×2, `230000021576`×2, `239010008076`×2, `239010005841`×2, `230000003950`×2, `230000011466`×1, `239010002999`×1, `239010005453`×1

### `db2:account.CUST_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

### `db2:ctrans.CUST_ID`
- Null rate trong sample: 0%
- Distinct ≈12; top: `50855`×6, `51547`×3, `51373`×2, `51067`×1, `50565`×1, `50672`×1, `51449`×1, `50426`×1

### `db2:debt.CUST_ID`
- Null rate trong sample: 0%
- Distinct ≈9; top: `00097`×5, `00469`×4, `00043`×3, `00310`×2, `00656`×2, `50193`×1, `00481`×1, `00248`×1

### `db2:inv_hdr.CUST_ID`
- Null rate trong sample: 0%
- Distinct ≈19; top: `51436`×2, `51345`×1, `50361`×1, `51428`×1, `51325`×1, `51272`×1, `00032`×1, `51112`×1

### `db2:inv_iss.CUST_ID`
- Null rate trong sample: 5%
- Distinct ≈19; top: `230000000001`×1, `230000000437`×1, `230000000468`×1, `230000000506`×1, `230000000605`×1, `230000001032`×1, `230000001072`×1, `230000001074`×1

### `db2:pmcrdiss.CUST_ID`
- Null rate trong sample: 5%
- Distinct ≈1; top: `230000000001`×19

### `db2:pmcrdrcv.CUST_ID`
- Null rate trong sample: 45%
- Distinct ≈5; top: `230000004963`×5, `239020002189`×2, `230000032428`×2, `230000021953`×1, `239020003306`×1

### `db2:webrpt_rfm_snapshot.cust_id`
- Null rate trong sample: 0%
- Distinct ≈20; top: `230000012826`×1, `230000000935`×1, `239010001245`×1, `230000006449`×1, `239010004234`×1, `230000012877`×1, `239010005025`×1, `239010005165`×1

## Ghi chú thêm

- Mã khách hàng
