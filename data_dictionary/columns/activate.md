---
semantic_key: activate
title: activate
display_names:
- ACTIVATE
kind: flag
tables:
- ref: db2:pmcrdinf
  column: ACTIVATE
  type: bit
- ref: db2:pmcrdstk
  column: ACTIVATE
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Đã kích hoạt
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdinf.ACTIVATE: top=False(890), True(110)'
- 'db2:pmcrdstk.ACTIVATE: top=False(1000)'
---

# activate

**Semantic key:** `activate` · **Cột vật lý:** `ACTIVATE`

## Ý nghĩa nghiệp vụ

Cột ACTIVATE trên PMCRDINF, PMCRDSTK. db2:pmcrdinf: top False; db2:pmcrdstk: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `ACTIVATE` | bit | có dữ liệu |
| `db2:pmcrdstk` | `ACTIVATE` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.ACTIVATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:pmcrdstk.ACTIVATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Đã kích hoạt
