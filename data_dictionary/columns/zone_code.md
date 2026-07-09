---
semantic_key: zone_code
title: zone code
display_names:
- ZONE_CODE
kind: code
tables:
- ref: db2:hisrtpr
  column: ZONE_CODE
  type: char
- ref: db2:rdiscinf
  column: ZONE_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- MãZONE_CODE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:hisrtpr.ZONE_CODE: top=000(1000)'
- 'db2:rdiscinf.ZONE_CODE: top=000(1000)'
---

# zone code

**Semantic key:** `zone_code` · **Cột vật lý:** `ZONE_CODE`

## Ý nghĩa nghiệp vụ

Cột ZONE_CODE trên HISRTPR, RDISCINF. db2:hisrtpr: top 000; db2:rdiscinf: top 000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hisrtpr` | `ZONE_CODE` | char | có dữ liệu |
| `db2:rdiscinf` | `ZONE_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hisrtpr.ZONE_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `000`×20

### `db2:rdiscinf.ZONE_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `000`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- MãZONE_CODE
