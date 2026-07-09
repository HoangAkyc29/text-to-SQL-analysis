---
semantic_key: loyalty_card_master_id
title: Mã thẻ loyalty (master CSCARD/CRD_INFO)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db2:crd_info
  column: CARD_ID
  type: char
- ref: db2:cscard
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
- 'db2:crd_info.CARD_ID: top=A10000065244(2), A10000067846(2), A10000062955(2), A10000064687(2),
  A10000055196(2)'
- 'db2:cscard.CARD_ID: top=A10000065264(1), A10000047314(1), A10000055442(1), A10000070558(1),
  A10000061361(1)'
---

# Mã thẻ loyalty (master CSCARD/CRD_INFO)

**Semantic key:** `loyalty_card_master_id` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Định danh thẻ khách hàng thân thiết trên master CSCARD. Sample db2: prefix `A` (vd. A10000000003). Dùng join CRDTRANS/CRD_INFO, lọc VIP theo prefix E/F/H. Khác với CARD_ID trên STRANS (chỉ là thẻ quét trên bill, thường rỗng).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `CARD_ID` | char | có dữ liệu |
| `db2:cscard` | `CARD_ID` | char | Master thẻ — primary loyalty identifier |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `A10000000003`×1, `A10000000991`×1, `A10000002239`×1, `A10000002839`×1, `a10000003064`×1, `A10000003872`×1, `A10000004091`×1, `A10000004318`×1

### `db2:cscard.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `A10000000003`×1, `A10000000004`×1, `A10000000012`×1, `A10000000021`×1, `A10000000038`×1, `A10000000044`×1, `A10000000106`×1, `A10000000156`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
