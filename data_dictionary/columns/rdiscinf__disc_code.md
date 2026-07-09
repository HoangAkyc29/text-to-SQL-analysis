---
semantic_key: rdiscinf__disc_code
title: rdiscinf · disc code
display_names:
- DISC_CODE
kind: code
tables:
- ref: db2:rdiscinf
  column: DISC_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã chiết khấu
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISC_CODE
- 'db2:rdiscinf.DISC_CODE: top=000150418001(11), 000140818001(10), 000124122601(10),
  000122042702(10), 000130302004(9)'
---

# rdiscinf · disc code

**Semantic key:** `rdiscinf__disc_code` · **Cột vật lý:** `DISC_CODE`

## Ý nghĩa nghiệp vụ

Cột DISC_CODE trên RDISCINF. db2:rdiscinf: top 000117101803, 000117101802, 000117101804.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `DISC_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.DISC_CODE`
- Null rate trong sample: 0%
- Distinct ≈4; top: `000117101803`×13, `000117101802`×3, `000117101804`×3, `000117101801`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã chiết khấu
