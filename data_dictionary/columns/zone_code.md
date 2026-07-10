---
semantic_key: zone_code
title: Mã vùng / zone cửa hàng (ZONE_CODE)
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
- column_semantic_registry
- business_prose
---

# Mã vùng / zone cửa hàng (ZONE_CODE)

**Semantic key:** `zone_code` · **Cột vật lý:** `ZONE_CODE`

## Ý nghĩa nghiệp vụ

MãZONE_CODE. Dùng trong bảng HISRTPR, rule khuyến mãi / chiết khấu.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:hisrtpr` | `ZONE_CODE` | char | MãZONE_CODE |
| `db2:rdiscinf` | `ZONE_CODE` | char | MãZONE_CODE |

## Join

Thường join: `TRANS_NUM`
