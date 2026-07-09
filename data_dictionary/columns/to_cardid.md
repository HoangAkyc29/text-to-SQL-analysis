---
semantic_key: to_cardid
title: to cardid
display_names:
- TO_CARDID
kind: text
tables:
- ref: db2:pmcrdiss
  column: TO_CARDID
  type: char
- ref: db2:pmcrdstk
  column: TO_CARDID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Thẻ PM đích
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdiss.TO_CARDID: top=@P0000267923(1), @P0000233197(1), @P0000207345(1),
  @P0000453865(1), @P0000432161(1)'
- 'db2:pmcrdstk.TO_CARDID: top=@P0000005316(1), @P0000333366(1), @P0000359313(1),
  @P0000363625(1), @P0000280220(1)'
---

# to cardid

**Semantic key:** `to_cardid` · **Cột vật lý:** `TO_CARDID`

## Ý nghĩa nghiệp vụ

Cột TO_CARDID trên PMCRDISS, PMCRDSTK. db2:pmcrdiss: top @P0000245870, @P0000245873, @P0000245874; db2:pmcrdstk: top @P0000000010, @P0000000030, @P0000000036.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdiss` | `TO_CARDID` | char | có dữ liệu |
| `db2:pmcrdstk` | `TO_CARDID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdiss.TO_CARDID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `@P0000245870`×1, `@P0000245873`×1, `@P0000245874`×1, `@P0000245879`×1, `@P0000245883`×1, `@P0000245888`×1, `@P0000245891`×1, `@P0000245924`×1

### `db2:pmcrdstk.TO_CARDID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `@P0000000010`×1, `@P0000000030`×1, `@P0000000036`×1, `@P0000000056`×1, `@P0000000080`×1, `@P0000000120`×1, `@P0000000180`×1, `@P0000000260`×1

## Ghi chú thêm

- Thẻ PM đích
