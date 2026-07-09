---
semantic_key: pmcrdstk__fr_seri
title: pmcrdstk · fr seri
display_names:
- FR_SERI
kind: text
tables:
- ref: db2:pmcrdstk
  column: FR_SERI
  type: char
join_with: []
related_semantic_keys: []
facts:
- Seri thẻ PM từ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FR_SERI
- 'db2:pmcrdstk.FR_SERI: top=0005311(1), 0333365(1), 0359308(1), 0363624(1), 0280220(1)'
---

# pmcrdstk · fr seri

**Semantic key:** `pmcrdstk__fr_seri` · **Cột vật lý:** `FR_SERI`

## Ý nghĩa nghiệp vụ

Cột FR_SERI trên PMCRDSTK. db2:pmcrdstk: top 0000001, 0000011, 0000031.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdstk` | `FR_SERI` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdstk.FR_SERI`
- Null rate trong sample: 0%
- Distinct ≈20; top: `0000001`×1, `0000011`×1, `0000031`×1, `0000037`×1, `0000057`×1, `0000081`×1, `0000121`×1, `0000181`×1

## Ghi chú thêm

- Seri thẻ PM từ
