---
semantic_key: fr_cardid
title: fr cardid
display_names:
- FR_CARDID
kind: text
tables:
- ref: db2:pmcrdiss
  column: FR_CARDID
  type: char
- ref: db2:pmcrdstk
  column: FR_CARDID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Thẻ PM nguồn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdiss.FR_CARDID: top=@P0000267923(1), @P0000233197(1), @P0000207344(1),
  @P0000453865(1), @P0000432156(1)'
- 'db2:pmcrdstk.FR_CARDID: top=@P0000005311(1), @P0000333365(1), @P0000359308(1),
  @P0000363624(1), @P0000280220(1)'
---

# fr cardid

**Semantic key:** `fr_cardid` · **Cột vật lý:** `FR_CARDID`

## Ý nghĩa nghiệp vụ

Cột FR_CARDID trên PMCRDISS, PMCRDSTK. db2:pmcrdiss: top @P0000245867, @P0000245871, @P0000245874; db2:pmcrdstk: top @P0000000001, @P0000000011, @P0000000031.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdiss` | `FR_CARDID` | char | có dữ liệu |
| `db2:pmcrdstk` | `FR_CARDID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdiss.FR_CARDID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `@P0000245867`×1, `@P0000245871`×1, `@P0000245874`×1, `@P0000245875`×1, `@P0000245880`×1, `@P0000245884`×1, `@P0000245889`×1, `@P0000245892`×1

### `db2:pmcrdstk.FR_CARDID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `@P0000000001`×1, `@P0000000011`×1, `@P0000000031`×1, `@P0000000037`×1, `@P0000000057`×1, `@P0000000081`×1, `@P0000000121`×1, `@P0000000181`×1

## Ghi chú thêm

- Thẻ PM nguồn
