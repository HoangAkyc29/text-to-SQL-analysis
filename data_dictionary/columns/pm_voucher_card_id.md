---
semantic_key: pm_voucher_card_id
title: Mã thẻ khách hàng thân thiết (CARD_ID)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: CARD_ID
  type: char
- ref: db2:pmcrdrcv
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

# Mã thẻ khách hàng thân thiết (CARD_ID)

**Semantic key:** `pm_voucher_card_id` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng. Dùng trong master thẻ PM / voucher, bảng PMCRDRCV.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:pmcrdrcv` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`
