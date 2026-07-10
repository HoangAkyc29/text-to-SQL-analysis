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
- column_semantic_registry
- business_prose
---

# Thẻ trong giao dịch tích điểm (CRDTRANS)

**Semantic key:** `loyalty_tx_card_id` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Thẻ trong giao dịch tích điểm CRDTRANS — luôn populate (khác STRANS.CARD_ID). Prefix E thường gắn VIP.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:crdtrans` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:crdtrans_tmp` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
