---
semantic_key: pm_voucher_card_id
title: pm voucher card id
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
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdinf.CARD_ID: top=@P0000006441(1), @P0000014691(1), @P0000327175(1), @P0000455333(1),
  @P0000210534(1)'
- 'db2:pmcrdrcv.CARD_ID: top=@P0000569056(1), @P0000567532(1), @P0000571426(1), @P0000569908(1),
  @P0000567503(1)'
---

# pm voucher card id

**Semantic key:** `pm_voucher_card_id` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Cột CARD_ID trên PMCRDINF, PMCRDRCV. db2:pmcrdinf: prefix  (vd. @P0000000001); db2:pmcrdrcv: prefix  (vd. @P0000554817).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `CARD_ID` | char | có dữ liệu |
| `db2:pmcrdrcv` | `CARD_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `@P0000000001`×1, `@P0000000002`×1, `@P0000000003`×1, `@P0000000004`×1, `@P0000000005`×1, `@P0000000006`×1, `@P0000000007`×1, `@P0000000008`×1

### `db2:pmcrdrcv.CARD_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `@P0000554817`×1, `@P0000554835`×1, `@P0000554836`×1, `@P0000555175`×1, `@P0000555176`×1, `@P0000555183`×1, `@P0000555199`×1, `@P0000555228`×1

## Join

Thường join: `TRANS_NUM`, `CUST_ID`

## Ghi chú thêm

- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
