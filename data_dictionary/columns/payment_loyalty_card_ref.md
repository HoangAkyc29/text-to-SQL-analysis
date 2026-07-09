---
semantic_key: payment_loyalty_card_ref
title: Thẻ loyalty trên dòng thanh toán (PMTRANS)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db1:pmtrans
  column: CARD_ID
  type: char
- ref: db2:pmtrans
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
- 'db1:pmtrans.CARD_ID: top=@P0000545891(1), @P0000546039(1), @P0000542903(1), @P0000533566(1),
  @P0000545260(1)'
- 'db2:pmtrans.CARD_ID: top=@P0000567387(1), @P0000567086(1), @P0000569046(1), @P0000570771(1),
  @P0000557002(1)'
---

# Thẻ loyalty trên dòng thanh toán (PMTRANS)

**Semantic key:** `payment_loyalty_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Cột CARD_ID trên PMTRANS. db1:pmtrans: sample toàn rỗng; db2:pmtrans: sample toàn rỗng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `CARD_ID` | char | Thẻ quét trên giao dịch — sample thường rỗng |
| `db2:pmtrans` | `CARD_ID` | char | Thẻ quét trên giao dịch — sample thường rỗng |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
