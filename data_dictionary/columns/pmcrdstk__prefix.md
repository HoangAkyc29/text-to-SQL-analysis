---
semantic_key: pmcrdstk__prefix
title: pmcrdstk · prefix
display_names:
- PREFIX
kind: text
tables:
- ref: db2:pmcrdstk
  column: PREFIX
  type: char
join_with: []
related_semantic_keys: []
facts:
- Prefix seri thẻ PM (@P)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PREFIX
- 'db2:pmcrdstk.PREFIX: top=@P(1000)'
---

# pmcrdstk · prefix

**Semantic key:** `pmcrdstk__prefix` · **Cột vật lý:** `PREFIX`

## Ý nghĩa nghiệp vụ

Cột PREFIX trên PMCRDSTK. db2:pmcrdstk: top @P.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdstk` | `PREFIX` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdstk.PREFIX`
- Null rate trong sample: 0%
- Distinct ≈1; top: `@P`×20

## Ghi chú thêm

- Prefix seri thẻ PM (@P)
