---
semantic_key: custsumm__mobil
title: custsumm · mobil
display_names:
- Mobil
kind: text
tables:
- ref: db2:custsumm
  column: Mobil
  type: char
join_with: []
related_semantic_keys: []
facts:
- Di động
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for Mobil
- 'db2:custsumm.Mobil: top=0935345357(2), 0914352280(2), 0917981951(2), 0905033722(1),
  0364709998(1)'
---

# custsumm · mobil

**Semantic key:** `custsumm__mobil` · **Cột vật lý:** `Mobil`

## Ý nghĩa nghiệp vụ

Cột MOBIL trên CUSTSUMM. db2:custsumm: top 0905232710.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:custsumm` | `Mobil` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:custsumm.Mobil`
- Null rate trong sample: 95%
- Distinct ≈1; top: `0905232710`×1

## Ghi chú thêm

- Di động
