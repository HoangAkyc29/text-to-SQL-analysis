---
semantic_key: pmcrdstk__to_seri
title: pmcrdstk · to seri
display_names:
- TO_SERI
kind: text
tables:
- ref: db2:pmcrdstk
  column: TO_SERI
  type: char
join_with: []
related_semantic_keys: []
facts:
- Seri thẻ PM đến
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TO_SERI
- 'db2:pmcrdstk.TO_SERI: top=0005316(1), 0333366(1), 0359313(1), 0363625(1), 0280220(1)'
---

# pmcrdstk · to seri

**Semantic key:** `pmcrdstk__to_seri` · **Cột vật lý:** `TO_SERI`

## Ý nghĩa nghiệp vụ

Cột TO_SERI trên PMCRDSTK. db2:pmcrdstk: top 0000010, 0000030, 0000036.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdstk` | `TO_SERI` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdstk.TO_SERI`
- Null rate trong sample: 0%
- Distinct ≈20; top: `0000010`×1, `0000030`×1, `0000036`×1, `0000056`×1, `0000080`×1, `0000120`×1, `0000180`×1, `0000260`×1

## Ghi chú thêm

- Seri thẻ PM đến
