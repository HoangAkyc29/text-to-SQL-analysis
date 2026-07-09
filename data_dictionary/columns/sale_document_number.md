---
semantic_key: sale_document_number
title: Số chứng từ / bill — join header ↔ dòng ↔ thanh toán
display_names:
- TRANS_NUM
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: TRANS_NUM
  type: char
- ref: db1:pmtrans
  column: TRANS_NUM
  type: char
- ref: db1:strans
  column: TRANS_NUM
  type: char
- ref: db1:transhdr_arc
  column: TRANS_NUM
  type: char
- ref: db2:cash_st
  column: TRANS_NUM
  type: char
- ref: db2:crdtrans
  column: TRANS_NUM
  type: char
- ref: db2:crdtrans_tmp
  column: TRANS_NUM
  type: char
- ref: db2:ctrans
  column: TRANS_NUM
  type: char
- ref: db2:custhist
  column: TRANS_NUM
  type: char
- ref: db2:inv_iss
  column: TRANS_NUM
  type: char
- ref: db2:pmcrdiss
  column: TRANS_NUM
  type: char
- ref: db2:pmcrdrcv
  column: TRANS_NUM
  type: char
- ref: db2:pmcrdstk
  column: TRANS_NUM
  type: char
- ref: db2:pmtrans
  column: TRANS_NUM
  type: char
- ref: db2:st_order
  column: TRANS_NUM
  type: char
- ref: db2:strans
  column: TRANS_NUM
  type: char
- ref: db2:strans_tmp
  column: TRANS_NUM
  type: char
- ref: db2:suspend
  column: TRANS_NUM
  type: char
- ref: db2:transhdr
  column: TRANS_NUM
  type: char
join_with: []
related_semantic_keys: []
facts:
- Số chứng từ / bill; join header ↔ dòng ↔ thanh toán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.TRANS_NUM: top=000B52211701005231(1), 000B52211812000723(1), 000B52211912001731(1),
  000A12211603009896(1), 000BQ2212509004387(1)'
- 'db1:pmtrans.TRANS_NUM: top=000AV2212504009411(2), 902BM2212504000997(2), 000AV2212504008349(1),
  901AX2212504004944(1), 000AV2212504003078(1)'
- 'db1:strans.TRANS_NUM: top=901003202504000003(32), 901003202504000001(31), 000003202504000006(17),
  000003202504000001(14), 902003202504000002(12)'
- 'db1:transhdr_arc.TRANS_NUM: top=000001132106002089(1), 901AY2212505002307(1), 000AV2212306000026(1),
  000B52212011006058(1), 000BQ2212508005457(1)'
- 'db2:cash_st.TRANS_NUM: top=902BM0102606000052(4), 000BQ0102605000024(4), 000BE0102603000059(3),
  000BR0102604000045(3), 000BE0102512000008(3)'
- 'db2:crdtrans.TRANS_NUM: top=000BR2212606003714(1), 901AY2212607000170(1), 000BE2212606009610(1),
  000BE2212607001694(1), 000BR2212606001184(1)'
- 'db2:crdtrans_tmp.TRANS_NUM: top=000AV2212409009730(1), 000BE2212403001864(1), 000BE2212410006086(1),
  901AX2212403002158(1), 000AP2212406001609(1)'
- 'db2:ctrans.TRANS_NUM: top=000002112606000024(1), 000001132606001277(1), 000001132606001960(1),
  000001132607000100(1), 000001132606001407(1)'
- 'db2:custhist.TRANS_NUM: top=000001132403000481(4), 000001131903000269(3), 000001132208001368(3),
  000001132009001813(3), 000001132012000275(3)'
- 'db2:inv_iss.TRANS_NUM: top=000AV2212209000507(1), 000BR2212601001528(1), 000AP2212410003095(1),
  000AV2212501002926(1), 000BQ2212512008510(1)'
- 'db2:pmcrdiss.TRANS_NUM: top=000008241611000021(11), 000008241705000029(7), 000008241709000012(6),
  000008241604000028(6), 000008241610000013(5)'
- 'db2:pmcrdrcv.TRANS_NUM: top=000BE2212606002436(10), 000BR2212606003363(8), 000BR2212606005485(8),
  000BQ2212606003427(7), 000BQ2212607001926(7)'
- 'db2:pmcrdstk.TRANS_NUM: top=000008211611000021(7), 000008211608000030(6), 000008211608000022(6),
  000008211704000017(5), 000008211701000020(5)'
- 'db2:pmtrans.TRANS_NUM: top=901AY2212606000326(2), 901AX2212607001448(2), 000BQ2212606002137(1),
  000BQ2212606005278(1), 901AY2212606001881(1)'
- 'db2:st_order.TRANS_NUM: top=000003342606000173(77), 000003342606000119(49), 000003342606000017(37),
  000003342606000175(33), 000003342606000095(30)'
- 'db2:strans.TRANS_NUM: top=000003202606000002(32), 000003202606000003(14), 000003202606000001(14),
  000001132606001751(3), 000BQ2212606001143(2)'
- 'db2:strans_tmp.TRANS_NUM: top=902BM2212405004019(2), 000BE2212405006786(2), 000AP2212405004923(2),
  901AY2212405003304(2), 000BE2212405002918(2)'
- 'db2:suspend.TRANS_NUM: top=000AV2212301004997(2), 000AP2212311000096(2), 000BQ2212511008618(2),
  000B52212012006025(2), 000BE2212206006570(2)'
- 'db2:transhdr.TRANS_NUM: top=000BR2212606001539(1), 901AY2212607000090(1), 000BE2212606000680(1),
  000BE2212606006677(1), 000BR2212606004326(1)'
---

# Số chứng từ / bill — join header ↔ dòng ↔ thanh toán

**Semantic key:** `sale_document_number` · **Cột vật lý:** `TRANS_NUM`

## Ý nghĩa nghiệp vụ

TRANS_NUM liên kết TRANSHDR ↔ STRANS ↔ PMTRANS. Sample STRANS: 000001132605000001; PMTRANS prefix 000AB008/000AB222.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `TRANS_NUM` | char | có dữ liệu |
| `db1:pmtrans` | `TRANS_NUM` | char | có dữ liệu |
| `db1:strans` | `TRANS_NUM` | char | có dữ liệu |
| `db1:transhdr_arc` | `TRANS_NUM` | char | có dữ liệu |
| `db2:cash_st` | `TRANS_NUM` | char | có dữ liệu |
| `db2:crdtrans` | `TRANS_NUM` | char | có dữ liệu |
| `db2:crdtrans_tmp` | `TRANS_NUM` | char | có dữ liệu |
| `db2:ctrans` | `TRANS_NUM` | char | có dữ liệu |
| `db2:custhist` | `TRANS_NUM` | char | có dữ liệu |
| `db2:inv_iss` | `TRANS_NUM` | char | có dữ liệu |
| `db2:pmcrdiss` | `TRANS_NUM` | char | có dữ liệu |
| `db2:pmcrdrcv` | `TRANS_NUM` | char | có dữ liệu |
| `db2:pmcrdstk` | `TRANS_NUM` | char | có dữ liệu |
| `db2:pmtrans` | `TRANS_NUM` | char | có dữ liệu |
| `db2:st_order` | `TRANS_NUM` | char | có dữ liệu |
| `db2:strans` | `TRANS_NUM` | char | có dữ liệu |
| `db2:strans_tmp` | `TRANS_NUM` | char | có dữ liệu |
| `db2:suspend` | `TRANS_NUM` | char | có dữ liệu |
| `db2:transhdr` | `TRANS_NUM` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000008122511000015`×1, `000008122511000016`×1, `000008122511000017`×1, `000008122511000018`×1, `000008122511000019`×1, `000008122511000020`×1, `000008122511000021`×1, `000008122511000022`×1

### `db1:pmtrans.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈13; top: `901AX2212604002170`×2, `901AX2212604002172`×2, `901AX2212604002173`×2, `901AX2212604002175`×2, `901AX2212604002177`×2, `901AX2212604002178`×2, `901AX2212604002179`×2, `901AX2212604002171`×1

### `db1:strans.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈4; top: `000001132604000003`×10, `000001132604000121`×5, `000001132604000002`×4, `000001132604000001`×1

### `db1:transhdr_arc.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `901AX2212511002091`×1, `901AX2212511002092`×1, `901AX2212511002093`×1, `901AX2212511002094`×1, `901AX2212511002095`×1, `901AX2212511002096`×1, `901AX2212511002097`×1, `901AX2212511002098`×1

### `db2:cash_st.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈2; top: `000AA0102310000001`×11, `000AA0102507000001`×9

### `db2:crdtrans.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000008112606000001`×1, `000008112606000002`×1, `000008112606000003`×1, `000008112606000004`×1, `000008112606000005`×1, `000008112606000006`×1, `000008112606000007`×1, `000008112606000008`×1

### `db2:crdtrans_tmp.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000AB2212401000001`×1, `000AB2212401000004`×1, `000AB2212401000005`×1, `000AB2212401000008`×1, `000AB2212401000014`×1, `000AB2212401000018`×1, `000AB2212401000021`×1, `000AB2212401000022`×1

### `db2:ctrans.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000001132606000001`×1, `000001132606000002`×1, `000001132606000003`×1, `000001132606000004`×1, `000001132606000005`×1, `000001132606000010`×1, `000001132606000011`×1, `000001132606000012`×1

### `db2:custhist.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈16; top: `000001131911001055`×2, `000001132203001685`×2, `000001131801000973`×2, `000001131804000557`×2, `000001131811000002`×1, `000001132009000545`×1, `000001132202000557`×1, `000001132203001686`×1

### `db2:pmcrdiss.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000008211710000070`×1, `000008211710000071`×1, `000008211710000072`×1, `000008211710000073`×1, `000008211710000074`×1, `000008211710000075`×1, `000008211710000076`×1, `000008211710000077`×1

### `db2:pmcrdrcv.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈11; top: `000BQ2212606009220`×5, `902BM2212606001384`×2, `000BQ2212607001336`×2, `902BM2212606007082`×2, `000BQ2212606000933`×2, `000BR2212606002475`×2, `000BQ2212606007570`×1, `902BM2212607000497`×1

### `db2:pmcrdstk.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈4; top: `000008211212000026`×13, `000008211212000028`×5, `000008211212000027`×1, `000008211301000003`×1

### `db2:pmtrans.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000AB0082606000001`×1, `000AB0082606000002`×1, `000AB0082606000003`×1, `000AB2222606000001`×1, `000AB2222606000002`×1, `000AB2222606000003`×1, `000AB2222606000004`×1, `000AB2222606000005`×1

### `db2:st_order.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈2; top: `000003342606000002`×17, `000003342606000005`×3

### `db2:strans.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈4; top: `000001132606000004`×8, `000001132606000003`×7, `000001132606000002`×4, `000001132606000001`×1

### `db2:strans_tmp.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈6; top: `000002112405000001`×7, `000002112405000004`×5, `000002112405000006`×3, `000002112405000002`×2, `000002112405000005`×2, `000002112405000003`×1

### `db2:suspend.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈2; top: `000A12212007000003`×13, `000A12212007000004`×7

### `db2:transhdr.TRANS_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000001132606000001`×1, `000001132606000002`×1, `000001132606000003`×1, `000001132606000004`×1, `000001132606000005`×1, `000001132606000006`×1, `000001132606000007`×1, `000001132606000008`×1

## Ghi chú thêm

- Số chứng từ / bill; join header ↔ dòng ↔ thanh toán
