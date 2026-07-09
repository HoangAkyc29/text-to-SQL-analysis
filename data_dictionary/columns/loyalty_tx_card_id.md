---
semantic_key: loyalty_tx_card_id
title: Thẻ trong giao dịch tích điểm (CRDTRANS)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: CARD_ID
  type: char
- ref: db2:crdtrans
  column: CARD_ID
  type: char
- ref: db2:crdtrans_tmp
  column: CARD_ID
  type: char
join_with:
- TRANS_NUM
- CUST_ID
related_semantic_keys: []
facts:
- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.CARD_ID: top=E10000000327(4), e10000000151(3), e10000002905(3),
  E10000000484(3), E10000000309(3)'
- 'db2:crdtrans.CARD_ID: top=e10000003099(4), e10000001447(4), A10000064641(3), A10000063422(3),
  A10000074918(3)'
- 'db2:crdtrans_tmp.CARD_ID: top=e10000002414(4), e10000003758(3), A10000058403(3),
  E10000000981(3), e10000000939(3)'
---

# Thẻ trong giao dịch tích điểm (CRDTRANS)

**Semantic key:** `loyalty_tx_card_id` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Thẻ trong giao dịch CRDTRANS — luôn populate (khác STRANS.CARD_ID). Sample: prefix A/E; E… thường VIP. Join qua CARD_ID tới CSCARD/CRD_INFO.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `CARD_ID` | char | có dữ liệu |
| `db2:crdtrans` | `CARD_ID` | char | có dữ liệu |
| `db2:crdtrans_tmp` | `CARD_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈17; top: `A10000048143`×3, `A10000048482`×2, `E10000001433`×1, `A10000070543`×1, `A10000060971`×1, `E10000000810`×1, `E10000003778`×1, `E10000001437`×1

### `db2:crdtrans.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈19; top: `E10000004316`×2, `A10000077717`×1, `A10000077718`×1, `A10000077720`×1, `E10000004318`×1, `E10000004317`×1, `E10000004320`×1, `E10000004321`×1

### `db2:crdtrans_tmp.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈19; top: `A10000053937`×2, `A10000069787`×1, `E10000002892`×1, `E10000002001`×1, `A10000066743`×1, `A10000051145`×1, `A10000066806`×1, `E10000002846`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
