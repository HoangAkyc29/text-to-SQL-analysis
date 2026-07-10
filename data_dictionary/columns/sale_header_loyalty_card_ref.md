---
semantic_key: sale_header_loyalty_card_ref
title: Thẻ loyalty trên header bill (TRANSHDR / archive)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: CARD_ID
  type: char
- ref: db2:transhdr
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

# Thẻ loyalty trên header bill (TRANSHDR / archive)

**Semantic key:** `sale_header_loyalty_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Mã thẻ khách hàng thân thiết. Thẻ gắn trên header bill khi thanh toán có loyalty.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:transhdr` | `CARD_ID` | char | thẻ gắn trên header bill khi thanh toán có loyalty |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
