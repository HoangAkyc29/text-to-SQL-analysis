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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.CARD_ID: top=E10000001897(3), E10000003818(3), E10000003625(2), E10000001350(2),
  A10000061335(2)'
- 'db2:strans.CARD_ID: top=E10000002546(3), A10000075437(2), E10000004137(2), A10000068892(2),
  A10000063219(2)'
- 'db2:strans_tmp.CARD_ID: top=E10000003064(4), E10000002878(3), A10000063754(3),
  A10000064243(3), E10000000410(3)'
- 'db2:suspend.CARD_ID: top=e10000003064(5), E10000002749(3), f10000000014(3), e10000002279(2),
  e10000001360(2)'
---

# Thẻ loyalty ghi trên dòng bán (STRANS) — thường rỗng nếu KH không quét thẻ

**Semantic key:** `sale_line_loyalty_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Thẻ loyalty gắn trên dòng STRANS khi thanh toán có quét thẻ. Sample gần như luôn rỗng trong các bill bán lẻ thông thường — chỉ populate khi POS ghi nhận CARD_ID trên dòng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `CARD_ID` | char | Thẻ quét trên giao dịch — sample thường rỗng |
| `db2:strans` | `CARD_ID` | char | Thẻ quét trên giao dịch — sample thường rỗng |
| `db2:strans_tmp` | `CARD_ID` | char | có dữ liệu |
| `db2:suspend` | `CARD_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
