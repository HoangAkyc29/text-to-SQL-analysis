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
- column_semantic_registry
- business_prose
---

# Mã thẻ loyalty (master CSCARD/CRD_INFO)

**Semantic key:** `loyalty_card_master_id` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Định danh thẻ khách hàng thân thiết trên master CSCARD/CRD_INFO. Thẻ thường có prefix A (phổ thông) hoặc E/F/H (VIP). Dùng join CRDTRANS và tra cứu điểm; khác CARD_ID trên STRANS (chỉ khi quét thẻ lúc bán, thường để trống).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:cscard` | `CARD_ID` | char | mã thẻ chính trên master loyalty |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
