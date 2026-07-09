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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.CARD_ID: top=F10000000009(4), F10000000014(3), A10000054864(2),
  e10000000327(2), A10000054247(2)'
- 'db2:transhdr.CARD_ID: top=E10000002650(2), E10000003181(2), E10000002279(2), E10000003319(2),
  A10000072086(2)'
---

# Thẻ loyalty trên header bill (TRANSHDR / archive)

**Semantic key:** `sale_header_loyalty_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Cột CARD_ID trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: prefix A (vd. A10000064516); db2:transhdr: sample toàn rỗng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `CARD_ID` | char | có dữ liệu |
| `db2:transhdr` | `CARD_ID` | char | Thẻ quét trên giao dịch — sample thường rỗng |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.CARD_ID`
- Null rate trong sample: 35%
- Distinct ≈13; top: `A10000064516`×1, `A10000073670`×1, `A10000073072`×1, `E10000004037`×1, `E10000002980`×1, `E10000003935`×1, `A10000075044`×1, `A10000067985`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
