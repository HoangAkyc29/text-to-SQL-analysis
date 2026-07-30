---
semantic_key: sale_line_loyalty_card_ref
title: Thẻ loyalty ghi trên dòng bán (STRANS) — thường rỗng nếu KH không quét thẻ
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db1:strans
  column: CARD_ID
  type: char
- ref: db2:strans
  column: CARD_ID
  type: char
- ref: db2:strans_tmp
  column: CARD_ID
  type: char
- ref: db2:suspend
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

# Thẻ loyalty ghi trên dòng bán (STRANS) — thường rỗng nếu KH không quét thẻ

**Semantic key:** `sale_line_loyalty_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Thẻ loyalty gắn trên dòng STRANS khi POS ghi nhận quét thẻ lúc bán. Thường để trống với bill không loyalty.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `CARD_ID` | char | thẻ quét trên dòng bán — thường trống nếu khách không đưa thẻ |
| `db2:strans` | `CARD_ID` | char | thẻ quét trên dòng bán — thường trống nếu khách không đưa thẻ |
| `db2:strans_tmp` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:suspend` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |

## Join

Thường join hồ sơ khách: `CARD_ID` → `CSCARD` / `CUSTOMER` (không lấy `CUST_ID`
làm khóa chính khi bill/dòng đã mang thẻ).

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng.
- Dòng không quét thẻ thường để trống `CARD_ID` — lọc bỏ nếu brief chỉ hỏi khách có thẻ.
